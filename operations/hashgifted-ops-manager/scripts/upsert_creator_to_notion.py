#!/usr/bin/env python3
"""Upsert Hashgifted creator CRM rows into the Fig & Bloom Notion Creators DB.

Input: a JSON object or list of objects with fields such as:
{
  "name": "Creator Name",
  "handle": "creatorhandle",
  "instagram": "https://www.instagram.com/creatorhandle/",
  "location": "30km out of Brisbane",
  "stage": "Applied|Shortlisted|Selected|Complete|Manual Review",
  "followers": 12345,
  "engagement_rate": 0.034,
  "brand_fit": "Strong",
  "content_themes": ["Home", "Motherhood"],
  "visual_style": ["Natural Light", "Neutral"],
  "visual_evidence": "Observed feed notes..."
}

The script loads NOTION_API_KEY from /opt/data/.env if needed and matches existing
creators by Instagram URL, then Handle, then Creator Name. It is intentionally
idempotent and can be called by browser/cron workflows after every applicant review.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

NOTION_VERSION = "2025-09-03"
DEFAULT_CREATORS_DS = "221846a5-866d-43ef-bb19-6883fe1c2bdb"
DEFAULT_CREATORS_DB = "b5e1059f-543b-488b-ae19-3a3055dbc672"

SELECT_FIELDS = {
    "status": "Status",
    "stage": "Hashgifted Stage",
    "application_status": "Application Status",
    "decision": "Decision",
    "decision_confidence": "Decision Confidence",
    "tier": "Tier",
    "metro_area": "Metro Area",
    "metro_eligible": "Metro Eligible",
    "location_confidence": "Location Confidence",
    "visual_review_status": "Visual Review Status",
    "brand_fit": "Brand Fit",
    "content_quality": "Content Quality",
    "reel_ability": "Reel Ability",
    "audience_fit": "Audience Fit",
    "engagement_quality": "Engagement Quality",
    "brand_safety": "Brand Safety",
}
MULTI_FIELDS = {
    "content_themes": "Content Themes",
    "visual_style": "Visual Style",
}
TEXT_FIELDS = {
    "location": "Location",
    "delivery_eligibility_notes": "Delivery Eligibility Notes",
    "visual_evidence": "Visual Evidence",
    "fit_signals": "Fit Signals",
    "risk_notes": "Risk Notes",
    "notes": "Notes",
}
NUMBER_FIELDS = {
    "followers": "Followers",
    "engagement_rate": "Engagement Rate",
    "distance_from_metro_km": "Distance From Metro Km",
    "campaign_count": "Campaign Count",
    "selected_count": "Selected Count",
    "completed_count": "Completed Count",
    "creator_rating": "Creator Rating",
}
DATE_FIELDS = {
    "last_applied": "Last Applied",
    "last_reviewed": "Last Reviewed",
    "last_selected": "Last Selected",
    "last_completed": "Last Completed",
    "last_visual_review": "Last Visual Review",
    "last_contacted": "Last Contacted",
}


def load_env(path: str = "/opt/data/.env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def notion_headers() -> dict[str, str]:
    key = os.environ.get("NOTION_API_KEY")
    if not key:
        raise SystemExit("NOTION_API_KEY is not set")
    return {
        "Authorization": f"Bearer {key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def notion(method: str, path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"https://api.notion.com/v1{path}", data=data, headers=notion_headers(), method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"Notion {method} {path} failed HTTP {exc.code}: {body[:1200]}") from exc


def prop_text(prop: dict) -> str:
    typ = prop.get("type")
    if typ == "title":
        return "".join(x.get("plain_text", "") for x in prop.get("title", []))
    if typ == "rich_text":
        return "".join(x.get("plain_text", "") for x in prop.get("rich_text", []))
    if typ == "url":
        return prop.get("url") or ""
    return ""


def normalise_instagram(value: str | None) -> str:
    if not value:
        return ""
    v = value.strip().rstrip("/")
    if v.startswith("@"):
        v = f"https://www.instagram.com/{v[1:]}"
    elif re.fullmatch(r"[A-Za-z0-9_.]+", v):
        v = f"https://www.instagram.com/{v}"
    return v.rstrip("/")


def handle_from(record: dict[str, Any]) -> str:
    handle = str(record.get("handle") or "").strip().lstrip("@")
    if handle:
        return handle
    ig = normalise_instagram(record.get("instagram"))
    return ig.rstrip("/").split("/")[-1] if ig else ""


def infer_location(location: str) -> dict[str, Any]:
    raw = (location or "").strip()
    s = raw.lower()
    metro = None
    for candidate in ("Melbourne", "Sydney", "Brisbane"):
        if candidate.lower() in s:
            metro = candidate
            break
    km = None
    m = re.search(r"(\d+(?:\.\d+)?)\s*km", s)
    if m:
        km = float(m.group(1))
    if not metro:
        return {"metro_area": "Unknown", "metro_eligible": "Unconfirmed", "location_confidence": "Unknown"}
    # Fig & Bloom policy: a creator up to 30km out of Brisbane counts as Brisbane;
    # apply consistently to Melbourne/Sydney/Brisbane inferred metro locations.
    if km is not None and km > 30:
        return {"metro_area": metro, "metro_eligible": "Unconfirmed", "location_confidence": "Weak", "distance_from_metro_km": km}
    return {"metro_area": metro, "metro_eligible": "Likely", "location_confidence": "Likely", **({"distance_from_metro_km": km} if km is not None else {})}


def find_existing(creators_ds: str, record: dict[str, Any]) -> str | None:
    ig = normalise_instagram(record.get("instagram"))
    handle = handle_from(record).lower()
    name = str(record.get("name") or record.get("creator_name") or "").strip().lower()
    body = {"page_size": 100}
    cursor = None
    while True:
        if cursor:
            body["start_cursor"] = cursor
        data = notion("POST", f"/data_sources/{creators_ds}/query", body)
        for row in data.get("results", []):
            props = row.get("properties", {})
            row_ig = normalise_instagram(prop_text(props.get("Instagram", {}))).lower()
            row_handle = prop_text(props.get("Handle", {})).lstrip("@").lower()
            row_name = prop_text(props.get("Creator Name", {})).lower()
            if ig and row_ig == ig.lower():
                return row["id"]
            if handle and row_handle == handle:
                return row["id"]
            if name and row_name == name:
                return row["id"]
        if not data.get("has_more"):
            return None
        cursor = data.get("next_cursor")


def select_prop(value: Any) -> dict | None:
    if value in (None, ""):
        return None
    return {"select": {"name": str(value)}}


def rich_text(value: Any) -> dict | None:
    if value in (None, ""):
        return None
    return {"rich_text": [{"text": {"content": str(value)[:1900]}}]}


def build_props(raw: dict[str, Any]) -> dict:
    record = {**infer_location(str(raw.get("location") or "")), **raw}
    name = record.get("name") or record.get("creator_name")
    if not name:
        raise ValueError("record missing name/creator_name")
    handle = handle_from(record)
    ig = normalise_instagram(record.get("instagram") or handle)
    props: dict[str, dict] = {
        "Creator Name": {"title": [{"text": {"content": str(name)}}]},
        "Handle": {"rich_text": [{"text": {"content": handle}}]} if handle else {"rich_text": []},
    }
    if ig:
        props["Instagram"] = {"url": ig}
        props["Profile URL Source"] = {"url": ig}
    for src, notion_name in SELECT_FIELDS.items():
        prop = select_prop(record.get(src))
        if prop:
            props[notion_name] = prop
    for src, notion_name in MULTI_FIELDS.items():
        vals = record.get(src) or []
        if isinstance(vals, str):
            vals = [v.strip() for v in vals.split(",") if v.strip()]
        if vals:
            props[notion_name] = {"multi_select": [{"name": str(v)} for v in vals]}
    for src, notion_name in TEXT_FIELDS.items():
        prop = rich_text(record.get(src))
        if prop:
            props[notion_name] = prop
    for src, notion_name in NUMBER_FIELDS.items():
        if record.get(src) not in (None, ""):
            props[notion_name] = {"number": float(record[src])}
    for src, notion_name in DATE_FIELDS.items():
        if record.get(src):
            props[notion_name] = {"date": {"start": str(record[src])}}
    if record.get("mark_reviewed_today"):
        today = date.today().isoformat()
        props.setdefault("Last Reviewed", {"date": {"start": today}})
        props.setdefault("Last Visual Review", {"date": {"start": today}})
    return props


def load_records(path: str) -> list[dict[str, Any]]:
    if path == "-":
        text = sys.stdin.read()
    else:
        text = Path(path).read_text()
    data = json.loads(text)
    return data if isinstance(data, list) else [data]


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="JSON object/list, or - for stdin")
    parser.add_argument("--creators-ds", default=DEFAULT_CREATORS_DS)
    parser.add_argument("--creators-db", default=DEFAULT_CREATORS_DB)
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--dry-run", action="store_true", help="Build properties and match rows but do not write to Notion")
    args = parser.parse_args()

    out = {"created": 0, "updated": 0, "would_create": 0, "would_update": 0, "pages": [], "errors": []}
    for record in load_records(args.json_file):
        try:
            props = build_props(record)
            page_id = find_existing(args.creators_ds, record)
            if args.dry_run:
                if page_id:
                    out["would_update"] += 1
                else:
                    out["would_create"] += 1
                out["pages"].append({
                    "name": record.get("name") or record.get("creator_name"),
                    "page_id": page_id,
                    "properties": sorted(props.keys()),
                    "metro_area": props.get("Metro Area", {}).get("select", {}).get("name"),
                    "metro_eligible": props.get("Metro Eligible", {}).get("select", {}).get("name"),
                    "distance_from_metro_km": props.get("Distance From Metro Km", {}).get("number"),
                })
            elif page_id:
                notion("PATCH", f"/pages/{page_id}", {"properties": props})
                out["updated"] += 1
                out["pages"].append({"name": record.get("name") or record.get("creator_name"), "page_id": page_id})
            else:
                res = notion("POST", "/pages", {"parent": {"database_id": args.creators_db}, "properties": props})
                page_id = res["id"]
                out["created"] += 1
                out["pages"].append({"name": record.get("name") or record.get("creator_name"), "page_id": page_id})
            time.sleep(args.sleep)
        except Exception as exc:  # noqa: BLE001 - batch sync should continue
            out["errors"].append({"name": record.get("name") or record.get("creator_name"), "error": str(exc)[:500]})
    print(json.dumps(out, indent=2))
    if out["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
