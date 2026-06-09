"""Mida.so client — experiment list + results read.

VERIFIED (2026-06): Mida's published SDKs (mida-node/python/php/...) are
delivery-side only (assign variant, track event, feature flags). BUT the Mida
Public V2 API *does* expose a results endpoint:

    GET {base}/v2/project/{project_key}/experiment/{test_id}/result   -> conversion results

Base URL is region-specific:
    US: https://api-us.mida.so
    EU: https://api-eu.mida.so
Auth: the API key as a Bearer token (also accepted as x-api-key / api-key).
Docs: https://api-docs-lemon.vercel.app/docs/intro  (repo: github.com/mida-so/api-docs)

Because the exact result JSON shape is not fully pinned in the public docs, the
parser below is defensive: it normalises the common fields (variant, visitors,
conversions, revenue -> RPV/AOV, lift, significance) and keeps the raw payload
so a mismatch is visible rather than silently wrong. If the live shape differs,
adjust `_normalise_result` — do not invent fields.

FALLBACK — GA4 bridge: Mida forwards `mida_pageview`, `mida_execute`
(exposure) and `mida_conversion` events into GA4, each carrying the test
name + variant as event params. If the reporting API is unavailable or
MIDA_API_KEY is unset, `results_via_ga4_bridge` reconstructs RPV/AOV per
variant from GA4. This requires Mida's GA4 integration to be enabled and the
test/variant params registered as custom dimensions in GA4.
"""

import os

import requests

DEFAULT_BASE = "https://api-us.mida.so"


class MidaError(RuntimeError):
    pass


class MidaClient:
    def __init__(self, project_key=None, api_key=None, base_url=None, timeout=30):
        self.project_key = project_key or os.environ.get("MIDA_PROJECT_KEY")
        self.api_key = api_key or os.environ.get("MIDA_API_KEY")
        self.base_url = (base_url or os.environ.get("MIDA_API_BASE", DEFAULT_BASE)).rstrip("/")
        self.timeout = timeout

    @property
    def reporting_available(self):
        return bool(self.project_key and self.api_key)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key or "",
            "Content-Type": "application/json",
        }

    def _get(self, path):
        if not self.reporting_available:
            raise MidaError("MIDA_PROJECT_KEY and MIDA_API_KEY are required for the reporting API")
        url = f"{self.base_url}/v2/project/{self.project_key}{path}"
        resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        if resp.status_code == 404:
            raise MidaError(f"Mida 404 at {path} — endpoint/test not found")
        if resp.status_code >= 400:
            raise MidaError(f"Mida HTTP {resp.status_code}: {resp.text[:500]}")
        return resp.json()

    # ------------------------------------------------------------------ #
    # Experiments
    # ------------------------------------------------------------------ #
    def list_experiments(self):
        """Return list of experiments for the project. Normalised to dicts with
        at least {test_id, name, status}. Raw kept under "_raw"."""
        data = self._get("/experiment")
        if isinstance(data, list):
            items = data
        else:
            items = data.get("experiments") or data.get("data") or []
        out = []
        for it in items:
            out.append({
                "test_id": it.get("test_id") or it.get("id") or it.get("key"),
                "name": it.get("name") or it.get("title"),
                "status": (it.get("status") or it.get("state") or "").lower(),
                "_raw": it,
            })
        return out

    def get_results(self, test_id):
        """Pull conversion results for one experiment, normalised per variant."""
        data = self._get(f"/experiment/{test_id}/result")
        return self._normalise_result(test_id, data)

    @staticmethod
    def _normalise_result(test_id, data):
        # The results payload typically carries per-variant counters. We read the
        # common shapes and derive RPV / AOV / lift where the inputs exist.
        variants_raw = (
            data.get("variants")
            or data.get("results")
            or data.get("variations")
            or []
        )
        variants = []
        for v in variants_raw:
            visitors = _num(v.get("visitors") or v.get("unique_visitors") or v.get("sessions"))
            conversions = _num(v.get("conversions") or v.get("goals") or v.get("orders"))
            revenue = _num(v.get("revenue") or v.get("total_revenue"))
            rpv = (revenue / visitors) if visitors else None
            aov = (revenue / conversions) if conversions else None
            cr = (conversions / visitors) if visitors else None
            variants.append({
                "variant": v.get("name") or v.get("variant") or v.get("key"),
                "is_control": bool(v.get("is_control") or v.get("control")),
                "visitors": visitors,
                "conversions": conversions,
                "revenue": revenue,
                "rpv": _round(rpv),
                "aov": _round(aov),
                "cr": _round(cr, 4),
                "lift_pct": _num(v.get("lift") or v.get("improvement")),
                "significance": v.get("significance") or v.get("confidence"),
            })
        return {
            "test_id": test_id,
            "variants": variants,
            "winner": data.get("winner"),
            "is_significant": _coerce_bool(data.get("is_significant") or data.get("significant")),
            "_raw": data,
            "_source": "mida_api",
        }

    # ------------------------------------------------------------------ #
    # GA4 bridge fallback
    # ------------------------------------------------------------------ #
    def results_via_ga4_bridge(self, ga4_client, test_name, start_date, end_date,
                               variant_dim="customEvent:mida_variant",
                               test_dim="customEvent:mida_test_name"):
        """Reconstruct per-variant RPV/AOV from Mida's GA4 bridge events.

        Reads `mida_conversion` events grouped by variant, with eventValue as
        revenue and conversions = event count, plus `mida_execute` exposure for
        visitor counts. Dimension names assume the standard Mida->GA4 params are
        registered as custom dimensions; override if your GA4 setup differs.
        """
        exposure = ga4_client.run_report(
            dimensions=[variant_dim, test_dim],
            metrics=["eventCount"],
            start_date=start_date,
            end_date=end_date,
            dimension_filter=ga4_client.event_name_filter(["mida_execute"]),
        )
        conv = ga4_client.run_report(
            dimensions=[variant_dim, test_dim],
            metrics=["eventCount", "eventValue"],
            start_date=start_date,
            end_date=end_date,
            dimension_filter=ga4_client.event_name_filter(["mida_conversion"]),
        )
        visitors = {r[variant_dim]: _num(r["eventCount"])
                    for r in exposure if r.get(test_dim) == test_name}
        variants = {}
        for r in conv:
            if r.get(test_dim) != test_name:
                continue
            name = r[variant_dim]
            conversions = _num(r["eventCount"])
            revenue = _num(r["eventValue"])
            vis = visitors.get(name, 0)
            variants[name] = {
                "variant": name,
                "visitors": vis,
                "conversions": conversions,
                "revenue": revenue,
                "rpv": _round((revenue / vis) if vis else None),
                "aov": _round((revenue / conversions) if conversions else None),
                "cr": _round((conversions / vis) if vis else None, 4),
                "lift_pct": None,
                "significance": None,
            }
        return {
            "test_id": None,
            "test_name": test_name,
            "variants": list(variants.values()),
            "winner": None,
            "is_significant": None,
            "_source": "ga4_bridge",
        }


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _round(x, ndigits=2):
    return round(x, ndigits) if isinstance(x, (int, float)) else None


def _coerce_bool(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        return x.strip().lower() in ("true", "yes", "1", "significant")
    return None
