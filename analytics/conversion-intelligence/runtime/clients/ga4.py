"""GA4 Data API client (read-only).

Reads the locked funnel (see funnel.py) and page/segment metrics from the
Google Analytics Data API v1beta using a service account. Read-only: this
client never touches Analytics configuration.

Auth: a GCP service account JSON with the "Viewer" role on the GA4 property.
Provide it via GA4_SERVICE_ACCOUNT_JSON, which may be either a path to the
JSON file or the raw JSON string (handy for secret managers / env injection).

Returns plain dicts/lists (JSON-serialisable) so the orchestrator and the
Notion ledger never need to know about protobuf types.
"""

import json
import os

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Filter,
        FilterExpression,
        Metric,
        RunReportRequest,
    )
    from google.oauth2 import service_account
    _IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - import guard
    _IMPORT_ERROR = exc

from funnel import FUNNEL_STEPS, GA4_EVENTS, step_by_event, transition_label

READONLY_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"

# Segment dimensions we always slice by. Kept small to stay well inside API
# limits while still answering "where is the bleed, and for whom".
DEFAULT_SEGMENTS = ["deviceCategory", "sessionDefaultChannelGroup", "landingPagePlusQueryString"]


class GA4Client:
    def __init__(self, property_id=None, service_account_json=None):
        if _IMPORT_ERROR is not None:
            raise RuntimeError(
                "google-analytics-data not installed. `pip install -r requirements.txt`. "
                f"Original error: {_IMPORT_ERROR}"
            )
        self.property_id = property_id or os.environ.get("GA4_PROPERTY_ID")
        if not self.property_id:
            raise ValueError("GA4_PROPERTY_ID is required")
        raw = service_account_json or os.environ.get("GA4_SERVICE_ACCOUNT_JSON")
        if not raw:
            raise ValueError("GA4_SERVICE_ACCOUNT_JSON is required (path or raw JSON)")
        info = self._load_credentials_info(raw)
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=[READONLY_SCOPE]
        )
        self._client = BetaAnalyticsDataClient(credentials=creds)

    @staticmethod
    def _load_credentials_info(raw):
        raw = raw.strip()
        if raw.startswith("{"):
            return json.loads(raw)
        with open(os.path.expanduser(raw), "r", encoding="utf-8") as fh:
            return json.load(fh)

    @property
    def _property(self):
        return f"properties/{self.property_id}"

    # ------------------------------------------------------------------ #
    # Funnel
    # ------------------------------------------------------------------ #
    def funnel_report(self, start_date, end_date, segments=None, compare_to=None):
        """Funnel for one window, optionally with a pre/post comparison window.

        Returns:
            {
              "window": {"start": ..., "end": ...},
              "steps": [ {step, label, ga4_event, sessions}, ... ],
              "transitions": [ {from, to, label, dropoff_sessions, dropoff_pct}, ... ],
              "segments": [ {segment dims..., steps: {...}}, ... ],
              "compare": <same shape or None>,
            }
        """
        segments = segments or DEFAULT_SEGMENTS
        current = self._funnel_for_window(start_date, end_date, segments)
        result = {
            "window": {"start": start_date, "end": end_date},
            **current,
            "compare": None,
        }
        if compare_to:
            c_start, c_end = compare_to
            prev = self._funnel_for_window(c_start, c_end, segments)
            result["compare"] = {"window": {"start": c_start, "end": c_end}, **prev}
            self._attach_deltas(result["transitions"], prev["transitions"])
        return result

    def _funnel_for_window(self, start_date, end_date, segments):
        # One report: sessions by eventName, sliced by segment dims, filtered to
        # the five funnel events. "sessions" filtered by eventName == sessions in
        # which that event occurred, our proxy for "reached this step".
        event_filter = FilterExpression(
            filter=Filter(
                field_name="eventName",
                in_list_filter=Filter.InListFilter(values=list(GA4_EVENTS)),
            )
        )
        request = RunReportRequest(
            property=self._property,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="eventName")] + [Dimension(name=s) for s in segments],
            metrics=[Metric(name="sessions"), Metric(name="eventCount")],
            dimension_filter=event_filter,
            limit=100000,
        )
        response = self._client.run_report(request)

        totals = {s.key: 0 for s in FUNNEL_STEPS}
        seg_rows = {}
        for row in response.rows:
            event_name = row.dimension_values[0].value
            step = step_by_event(event_name)
            if step is None:
                continue
            sessions = int(row.metric_values[0].value or 0)
            totals[step.key] += sessions

            seg_key = tuple(dv.value for dv in row.dimension_values[1:])
            bucket = seg_rows.setdefault(
                seg_key,
                {**{seg: seg_key[i] for i, seg in enumerate(segments)},
                 "steps": {s.key: 0 for s in FUNNEL_STEPS}},
            )
            bucket["steps"][step.key] += sessions

        steps = [
            {"step": s.key, "label": s.label, "ga4_event": s.ga4_event, "sessions": totals[s.key]}
            for s in FUNNEL_STEPS
        ]
        transitions = self._transitions(totals)
        return {
            "steps": steps,
            "transitions": transitions,
            "segments": sorted(
                seg_rows.values(),
                key=lambda b: b["steps"][FUNNEL_STEPS[0].key],
                reverse=True,
            ),
        }

    @staticmethod
    def _transitions(totals):
        out = []
        for a, b in zip(FUNNEL_STEPS, FUNNEL_STEPS[1:]):
            top = totals[a.key]
            bottom = totals[b.key]
            lost = max(top - bottom, 0)
            pct = (lost / top * 100.0) if top else 0.0
            out.append({
                "from": a.key,
                "to": b.key,
                "label": transition_label(a.key, b.key),
                "from_sessions": top,
                "to_sessions": bottom,
                "dropoff_sessions": lost,
                "dropoff_pct": round(pct, 2),
            })
        return out

    @staticmethod
    def _attach_deltas(current_transitions, prev_transitions):
        prev_by_key = {(t["from"], t["to"]): t for t in prev_transitions}
        for t in current_transitions:
            prev = prev_by_key.get((t["from"], t["to"]))
            if prev:
                t["dropoff_pct_delta"] = round(t["dropoff_pct"] - prev["dropoff_pct"], 2)
            else:
                t["dropoff_pct_delta"] = None

    # ------------------------------------------------------------------ #
    # Generic metric read (used by the Mida GA4 bridge and ad-hoc reads)
    # ------------------------------------------------------------------ #
    def run_report(self, dimensions, metrics, start_date, end_date,
                   dimension_filter=None, limit=100000):
        """Thin pass-through returning rows as list[dict]. Read-only."""
        request = RunReportRequest(
            property=self._property,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
            dimension_filter=dimension_filter,
            limit=limit,
        )
        response = self._client.run_report(request)
        rows = []
        for row in response.rows:
            record = {}
            for i, d in enumerate(dimensions):
                record[d] = row.dimension_values[i].value
            for i, m in enumerate(metrics):
                record[m] = row.metric_values[i].value
            rows.append(record)
        return rows

    @staticmethod
    def event_name_filter(values):
        """Build a dimension_filter for run_report on eventName in values."""
        return FilterExpression(
            filter=Filter(
                field_name="eventName",
                in_list_filter=Filter.InListFilter(values=list(values)),
            )
        )
