"""Notion ledger client — the observability layer.

Direct Notion REST API (https://api.notion.com/v1) using an internal
integration token. Talks to three databases:

    NOTION_DB_HYPOTHESES   CRO — Hypotheses
    NOTION_DB_TESTS        CRO — Tests
    NOTION_DB_RUNLOG       CRO — Run Log

Writes are idempotent:
  * Hypotheses are keyed on a "Dedup key" (funnel transition + hypothesis slug).
  * Tests are keyed on "Mida experiment key".
A re-run updates the existing record in place instead of creating a duplicate.

NOTE: the integration token must be shared on the parent page so it can see and
write these databases (Notion connections are not automatic). See README.
"""

import os

import requests

API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionError(RuntimeError):
    pass


class NotionLedger:
    def __init__(self, token=None, db_hypotheses=None, db_tests=None, db_runlog=None, timeout=30):
        self.token = token or os.environ.get("NOTION_TOKEN")
        self.db_hypotheses = db_hypotheses or os.environ.get("NOTION_DB_HYPOTHESES")
        self.db_tests = db_tests or os.environ.get("NOTION_DB_TESTS")
        self.db_runlog = db_runlog or os.environ.get("NOTION_DB_RUNLOG")
        self.timeout = timeout
        if not self.token:
            raise ValueError("NOTION_TOKEN is required")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def _request(self, method, path, payload=None):
        resp = requests.request(
            method, f"{API}{path}", headers=self._headers(),
            json=payload, timeout=self.timeout,
        )
        if resp.status_code >= 400:
            raise NotionError(f"Notion HTTP {resp.status_code} on {method} {path}: {resp.text[:500]}")
        return resp.json()

    # ------------------------------------------------------------------ #
    # Generic find-by-property (idempotency support)
    # ------------------------------------------------------------------ #
    def _find_by_rich_text(self, db_id, prop, value):
        payload = {
            "filter": {"property": prop, "rich_text": {"equals": value}},
            "page_size": 1,
        }
        data = self._request("POST", f"/databases/{db_id}/query", payload)
        results = data.get("results", [])
        return results[0] if results else None

    # ------------------------------------------------------------------ #
    # Hypotheses
    # ------------------------------------------------------------------ #
    def upsert_hypothesis(self, hypo):
        """Create or update a hypothesis. `hypo` is a dict; see loop.py for the
        shape. Idempotent on hypo["dedup_key"]. Returns the page object."""
        props = {
            "Title": _title(hypo["title"]),
            "Funnel step": _select(hypo.get("funnel_step")),
            "Friction signal": _rich(hypo.get("friction_signal")),
            "Hypothesis": _rich(hypo.get("hypothesis")),
            "Evidence": _rich(hypo.get("evidence")),
            "Expected metric": _rich(hypo.get("expected_metric")),
            "Impact": _number(hypo.get("impact")),
            "Confidence": _number(hypo.get("confidence")),
            "Ease": _number(hypo.get("ease")),
            "Priority": _number(hypo.get("priority")),
            "Status": _select(hypo.get("status", "Backlog")),
            "Owner agent": _rich(hypo.get("owner", "CRO")),
            "Dedup key": _rich(hypo["dedup_key"]),
        }
        props = _drop_empty(props)
        existing = self._find_by_rich_text(self.db_hypotheses, "Dedup key", hypo["dedup_key"])
        if existing:
            # Don't overwrite a human/agent decision once it's past Backlog.
            if _read_select(existing, "Status") not in (None, "Backlog"):
                props.pop("Status", None)
            return self._request("PATCH", f"/pages/{existing['id']}", {"properties": props})
        return self._request("POST", "/pages", {
            "parent": {"database_id": self.db_hypotheses},
            "properties": props,
        })

    # ------------------------------------------------------------------ #
    # Tests
    # ------------------------------------------------------------------ #
    def upsert_test(self, test):
        """Create or update a test record, idempotent on Mida experiment key."""
        props = {
            "Title": _title(test["title"]),
            "Mida experiment key": _rich(test.get("mida_key")),
            "Variants": _rich(test.get("variants")),
            "Primary metric": _rich(test.get("primary_metric")),
            "Segment": _rich(test.get("segment")),
            "Start": _date(test.get("start")),
            "End": _date(test.get("end")),
            "Lift %": _number(test.get("lift_pct")),
            "RPV": _number(test.get("rpv")),
            "AOV": _number(test.get("aov")),
            "Significance": _select(test.get("significance")),
            "Decision": _select(test.get("decision")),
            "Decided date": _date(test.get("decided_date")),
        }
        if test.get("linked_hypothesis_id"):
            props["Linked hypothesis"] = {"relation": [{"id": test["linked_hypothesis_id"]}]}
        props = _drop_empty(props)
        existing = self._find_by_rich_text(self.db_tests, "Mida experiment key", test.get("mida_key", ""))
        if existing and test.get("mida_key"):
            return self._request("PATCH", f"/pages/{existing['id']}", {"properties": props})
        return self._request("POST", "/pages", {
            "parent": {"database_id": self.db_tests},
            "properties": props,
        })

    # ------------------------------------------------------------------ #
    # Run log
    # ------------------------------------------------------------------ #
    def append_run_log(self, entry):
        """Append one heartbeat run record. Always creates a new row."""
        props = _drop_empty({
            "Title": _title(entry["title"]),
            "Run timestamp": _datetime(entry.get("run_timestamp")),
            "Run type": _select(entry.get("run_type", "Manual")),
            "Window": _rich(entry.get("window")),
            "Top drop-off found": _rich(entry.get("top_dropoff")),
            "Actions taken": _rich(entry.get("actions")),
            "Records touched": _rich(entry.get("records")),
            "Status": _select(entry.get("status", "OK")),
        })
        return self._request("POST", "/pages", {
            "parent": {"database_id": self.db_runlog},
            "properties": props,
        })


# ---------------------------------------------------------------------- #
# Property builders
# ---------------------------------------------------------------------- #
def _title(text):
    return {"title": [{"text": {"content": _clip(text, 2000)}}]} if text else None


def _rich(text):
    if text in (None, ""):
        return None
    return {"rich_text": [{"text": {"content": _clip(str(text), 2000)}}]}


def _select(name):
    return {"select": {"name": name}} if name else None


def _number(value):
    return {"number": value} if isinstance(value, (int, float)) else None


def _date(value):
    return {"date": {"start": value}} if value else None


def _datetime(value):
    return {"date": {"start": value}} if value else None


def _drop_empty(props):
    return {k: v for k, v in props.items() if v is not None}


def _clip(text, n):
    text = str(text)
    return text if len(text) <= n else text[: n - 1] + "…"


def _read_select(page, prop):
    try:
        sel = page["properties"][prop]["select"]
        return sel["name"] if sel else None
    except (KeyError, TypeError):
        return None
