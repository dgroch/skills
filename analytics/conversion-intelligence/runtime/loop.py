#!/usr/bin/env python3
"""Conversion Intelligence Programme — OODA loop orchestrator.

This is what the heartbeat calls. One run:

    Observe   -> GA4 funnel + Shopify outcomes for the window
    Detect    -> rank drop-off by lost-revenue impact (not just CVR)
    Hypothesise -> refresh a ranked, ICE-scored backlog in Notion
    Read tests -> pull live Mida experiment results; mark ship/kill/continue
    Decide+Log -> write the run summary to the Notion Run Log

Headless-safe: no interactive prompts. Fails soft — each stage is isolated, and
whatever happens, a Run Log entry is written (OK / Partial / Failed) so the loop
stays observable.

Usage:
    python loop.py --mode daily            # 1-day window, no compare
    python loop.py --mode weekly           # 7-day window + pre/post compare
    python loop.py --mode manual --window-days 14
    python loop.py --check                 # validate config/connectivity, no writes
    python loop.py --mode daily --dry-run  # compute + print, don't write to Notion
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback

# Make sibling modules importable whether run as `python loop.py` or `-m`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funnel import FUNNEL_STEPS  # noqa: E402
from playbook import play_for  # noqa: E402


# ---------------------------------------------------------------------- #
# Window helpers
# ---------------------------------------------------------------------- #
def _date(d):
    return d.strftime("%Y-%m-%d")


def compute_windows(mode, window_days, compare):
    today = dt.date.today()
    end = today - dt.timedelta(days=1)  # yesterday = last complete day
    days = window_days or (7 if mode == "weekly" else 1)
    start = end - dt.timedelta(days=days - 1)
    compare_window = None
    if compare or mode == "weekly":
        c_end = start - dt.timedelta(days=1)
        c_start = c_end - dt.timedelta(days=days - 1)
        compare_window = (_date(c_start), _date(c_end))
    return _date(start), _date(end), compare_window


# ---------------------------------------------------------------------- #
# Detection — rank transitions by revenue at risk
# ---------------------------------------------------------------------- #
def rank_dropoffs(funnel, aov):
    """Attach revenue-at-risk to each funnel transition and return them sorted
    worst-first.

    revenue_at_risk = lost_sessions * P(purchase | reached the 'to' step) * AOV
    For the final transition P(purchase|...) == 1, so it reduces to lost * AOV,
    which lines up with abandoned-checkout dollar value.
    """
    totals = {s["step"]: s["sessions"] for s in funnel["steps"]}
    purchase_sessions = totals.get("purchase", 0)
    ranked = []
    for t in funnel["transitions"]:
        to_sessions = totals.get(t["to"], 0)
        downstream_conv = (purchase_sessions / to_sessions) if to_sessions else 0.0
        if t["to"] == "purchase":
            downstream_conv = 1.0
        revenue_at_risk = round(t["dropoff_sessions"] * downstream_conv * (aov or 0.0), 2)
        ranked.append({**t, "downstream_conv": round(downstream_conv, 4),
                       "revenue_at_risk": revenue_at_risk})
    ranked.sort(key=lambda x: x["revenue_at_risk"], reverse=True)
    return ranked


# ---------------------------------------------------------------------- #
# Hypothesise
# ---------------------------------------------------------------------- #
def build_hypotheses(ranked, outcomes, top_n=3):
    """Turn the worst transitions into ICE-scored hypothesis dicts.

    Impact (1-5) comes from the revenue-at-risk rank so the backlog is ordered by
    lost dollars; confidence/ease come from the playbook priors.
    """
    candidates = [t for t in ranked if t["dropoff_sessions"] > 0][:top_n]
    n = len(candidates)
    hypos = []
    currency = outcomes.get("currency", "AUD")
    for i, t in enumerate(candidates):
        play = play_for((t["from"], t["to"]))
        if not play:
            continue
        impact = max(1, n - i)  # top candidate gets the highest impact
        confidence, ease = play["confidence"], play["ease"]
        priority = impact * confidence * ease
        evidence = (
            f"{t['dropoff_pct']}% drop-off at {t['label']} "
            f"({t['dropoff_sessions']} sessions lost); "
            f"~{currency} {t['revenue_at_risk']:.0f} revenue at risk this window."
        )
        if t["to"] == "purchase" and outcomes.get("abandoned"):
            ab = outcomes["abandoned"]
            evidence += (f" Abandoned checkouts: {ab['count']} worth "
                         f"{ab['currency']} {ab['lost_value']:.0f}.")
        hypos.append({
            "title": f"{t['label']}: {play['slug'].replace('-', ' ')}",
            "funnel_step": t["label"],
            "friction_signal": play["friction_signal"],
            "hypothesis": play["hypothesis"],
            "evidence": evidence,
            "expected_metric": play["expected_metric"],
            "impact": impact,
            "confidence": confidence,
            "ease": ease,
            "priority": priority,
            "status": "Backlog",
            "owner": os.environ.get("CRO_OWNER", "CRO"),
            "dedup_key": f"{t['label']}|{play['slug']}",
        })
    hypos.sort(key=lambda h: h["priority"], reverse=True)
    return hypos


# ---------------------------------------------------------------------- #
# Read tests
# ---------------------------------------------------------------------- #
def decide_test(result):
    """Map a normalised Mida result to (significance_label, decision)."""
    variants = result.get("variants", [])
    sig = result.get("is_significant")
    if sig is None:
        sig_label = "Reading"
    elif sig:
        sig_label = "Significant"
    else:
        sig_label = "Not significant"

    if not variants:
        return sig_label, "Pending"

    control = next((v for v in variants if v.get("is_control")), None)
    best = max(variants, key=lambda v: (v.get("rpv") or 0))
    if sig_label != "Significant":
        return sig_label, "Continue"
    if control is not None and best is control:
        return sig_label, "Kill"
    # A non-control variant wins with significance.
    lift = best.get("lift_pct")
    if lift is not None and lift < 0:
        return sig_label, "Kill"
    return sig_label, "Ship"


def summarise_variants(variants):
    parts = []
    for v in variants:
        rpv = v.get("rpv")
        parts.append(f"{v.get('variant')}: RPV {rpv if rpv is not None else 'n/a'}")
    return "; ".join(parts)


# ---------------------------------------------------------------------- #
# Orchestrator
# ---------------------------------------------------------------------- #
class Loop:
    def __init__(self, mode, dry_run=False):
        self.mode = mode
        self.dry_run = dry_run
        self.errors = []
        self.actions = []
        self.records = []

    def _safe(self, label, fn, *a, **k):
        try:
            return fn(*a, **k)
        except Exception as exc:  # noqa: BLE001 - fail soft, capture for Run Log
            self.errors.append(f"{label}: {exc}")
            traceback.print_exc()
            return None

    def run(self, start, end, compare):
        run_type = {"daily": "Daily observe", "weekly": "Weekly readout"}.get(self.mode, "Manual")
        window_str = f"{start}..{end}" + (f" vs {compare[0]}..{compare[1]}" if compare else "")
        print(f"[loop] mode={self.mode} window={window_str} dry_run={self.dry_run}")

        # --- clients (lazy; each optional so a missing cred degrades, not crashes)
        ga4 = self._safe("ga4_init", _init_ga4)
        shopify = self._safe("shopify_init", _init_shopify)
        mida = self._safe("mida_init", _init_mida)
        ledger = None if self.dry_run else self._safe("notion_init", _init_ledger)

        # --- OBSERVE
        funnel = None
        if ga4:
            funnel = self._safe("ga4_funnel", ga4.funnel_report, start, end,
                                compare_to=compare)
        outcomes = {"currency": "AUD"}
        if shopify:
            summary = self._safe("shopify_orders", shopify.orders_summary, start, end)
            if summary:
                outcomes.update(summary)
            ab = self._safe("shopify_abandoned", shopify.abandoned_checkouts, start, end)
            if ab:
                outcomes["abandoned"] = ab

        # --- DETECT
        ranked = []
        top_dropoff_str = "n/a"
        if funnel:
            ranked = rank_dropoffs(funnel, outcomes.get("aov", 0.0))
            if ranked:
                top = ranked[0]
                top_dropoff_str = (f"{top['label']} — {top['dropoff_pct']}% "
                                   f"({top['dropoff_sessions']} sessions, "
                                   f"~{outcomes.get('currency','AUD')} {top['revenue_at_risk']:.0f} at risk)")
                print(f"[detect] top drop-off: {top_dropoff_str}")
        else:
            self.errors.append("detect: no funnel data (GA4 unavailable)")

        # --- HYPOTHESISE
        hypos = build_hypotheses(ranked, outcomes) if ranked else []
        for h in hypos:
            if self.dry_run or not ledger:
                print(f"[hypo:dry] {h['title']} (priority {h['priority']})")
                continue
            page = self._safe("notion_hypo", ledger.upsert_hypothesis, h)
            if page:
                self.records.append(page.get("url", page.get("id", "")))
                self.actions.append(f"Hypothesis upserted: {h['title']} (P{h['priority']})")

        # --- READ TESTS
        self._read_tests(mida, ga4, ledger, hypos, start, end)

        # --- DECIDE + LOG
        status = self._status(funnel)
        self._log_run(ledger, run_type, window_str, top_dropoff_str, status)
        print(f"[loop] done status={status} errors={len(self.errors)}")
        return {
            "status": status,
            "window": window_str,
            "top_dropoff": top_dropoff_str,
            "hypotheses": len(hypos),
            "actions": self.actions,
            "errors": self.errors,
        }

    def _read_tests(self, mida, ga4, ledger, hypos, start, end):
        if not mida:
            return
        if mida.reporting_available:
            experiments = self._safe("mida_list", mida.list_experiments) or []
            for exp in experiments:
                status = exp.get("status", "")
                if status not in ("running", "live", "completed", "ended", "stopped"):
                    continue
                result = self._safe("mida_result", mida.get_results, exp["test_id"])
                if result:
                    self._write_test(ledger, exp, result, start, end)
        else:
            # GA4 bridge: needs explicit test names since Mida list isn't available.
            bridge_tests = [t.strip() for t in os.environ.get("MIDA_BRIDGE_TESTS", "").split(",") if t.strip()]
            if bridge_tests and ga4:
                for name in bridge_tests:
                    result = self._safe("mida_bridge", mida.results_via_ga4_bridge,
                                        ga4, name, start, end)
                    if result:
                        self._write_test(ledger, {"test_id": None, "name": name}, result, start, end)

    def _write_test(self, ledger, exp, result, start, end):
        sig_label, decision = decide_test(result)
        variants = result.get("variants", [])
        best = max(variants, key=lambda v: (v.get("rpv") or 0)) if variants else {}
        record = {
            "title": exp.get("name") or f"Mida test {exp.get('test_id')}",
            "mida_key": str(exp.get("test_id") or exp.get("name") or ""),
            "variants": summarise_variants(variants),
            "primary_metric": "RPV",
            "segment": "all",
            "start": start,
            "end": end,
            "lift_pct": best.get("lift_pct"),
            "rpv": best.get("rpv"),
            "aov": best.get("aov"),
            "significance": sig_label,
            "decision": decision,
            "decided_date": end if decision in ("Ship", "Kill") else None,
        }
        if self.dry_run or not ledger:
            print(f"[test:dry] {record['title']} -> {sig_label}/{decision} ({record['variants']})")
            return
        page = self._safe("notion_test", ledger.upsert_test, record)
        if page:
            self.records.append(page.get("url", page.get("id", "")))
            self.actions.append(f"Test read: {record['title']} -> {sig_label}/{decision}")

    def _status(self, funnel):
        if funnel is None:
            return "Failed"
        return "Partial" if self.errors else "OK"

    def _log_run(self, ledger, run_type, window_str, top_dropoff_str, status):
        actions = "; ".join(self.actions) if self.actions else "No write actions this run."
        if self.errors:
            actions += " | ERRORS: " + " | ".join(self.errors)
        entry = {
            "title": f"CRO run {dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M')}Z ({run_type})",
            "run_timestamp": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "run_type": run_type,
            "window": window_str,
            "top_dropoff": top_dropoff_str,
            "actions": actions,
            "records": "\n".join(r for r in self.records if r) or "—",
            "status": status,
        }
        if self.dry_run or not ledger:
            print("[runlog:dry] " + json.dumps(entry, indent=2))
            return
        self._safe("notion_runlog", ledger.append_run_log, entry)


# ---------------------------------------------------------------------- #
# Lazy client initialisers (imported here so --check can report clearly)
# ---------------------------------------------------------------------- #
def _init_ga4():
    from clients.ga4 import GA4Client
    return GA4Client()


def _init_shopify():
    from clients.shopify import ShopifyClient
    return ShopifyClient()


def _init_mida():
    from clients.mida import MidaClient
    return MidaClient()


def _init_ledger():
    from clients.notion_ledger import NotionLedger
    return NotionLedger()


# ---------------------------------------------------------------------- #
# --check: validate config without writing
# ---------------------------------------------------------------------- #
def run_check():
    print("[check] validating configuration and connectivity (read-only, no writes)")
    ok = True

    def report(name, fn):
        nonlocal ok
        try:
            fn()
            print(f"  ✓ {name}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"  ✗ {name}: {exc}")

    report("GA4 client init", _init_ga4)
    report("Shopify client init + shop_info", lambda: _init_shopify().shop_info())
    report("Notion ledger init", _init_ledger)

    mida = None
    try:
        mida = _init_mida()
        if mida.reporting_available:
            print("  • Mida reporting API configured (project key + API key present)")
        else:
            print("  • Mida reporting API NOT configured — will use GA4 bridge "
                  "(set MIDA_BRIDGE_TESTS) if available")
    except Exception as exc:  # noqa: BLE001
        print(f"  ✗ Mida client init: {exc}")
    print("[check] OK" if ok else "[check] one or more required clients failed")
    return 0 if ok else 1


# ---------------------------------------------------------------------- #
# Entry point
# ---------------------------------------------------------------------- #
def main(argv=None):
    parser = argparse.ArgumentParser(description="Conversion Intelligence loop")
    parser.add_argument("--mode", choices=["daily", "weekly", "manual"], default="daily")
    parser.add_argument("--window-days", type=int, default=None)
    parser.add_argument("--compare", action="store_true", help="force a pre/post compare window")
    parser.add_argument("--dry-run", action="store_true", help="compute + print, no Notion writes")
    parser.add_argument("--check", action="store_true", help="validate config/connectivity and exit")
    args = parser.parse_args(argv)

    _load_dotenv()

    if args.check:
        return run_check()

    start, end, compare = compute_windows(args.mode, args.window_days, args.compare)
    loop = Loop(mode=args.mode, dry_run=args.dry_run)
    result = loop.run(start, end, compare)
    # Non-zero exit on hard failure so the heartbeat can alert.
    return 0 if result["status"] != "Failed" else 1


def _load_dotenv():
    """Best-effort .env loader so a manual run picks up config/.env without a hard
    dependency on python-dotenv."""
    for path in ("config/.env", ".env",
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", ".env")):
        if os.path.exists(path):
            try:
                from dotenv import load_dotenv
                load_dotenv(path)
            except Exception:
                _manual_dotenv(path)
            return


def _manual_dotenv(path):
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


if __name__ == "__main__":
    raise SystemExit(main())
