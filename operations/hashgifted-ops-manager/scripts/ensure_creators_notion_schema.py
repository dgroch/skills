#!/usr/bin/env python3
"""Ensure the Hashgifted/Fig & Bloom Notion Creators data source has lifecycle fields.

This script is safe to rerun: it only adds missing properties and never removes or renames
existing properties. It uses the Notion 2025 data_sources API and loads NOTION_API_KEY
from /opt/data/.env when the process environment does not already provide it.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

NOTION_VERSION = "2025-09-03"
DEFAULT_CREATORS_DS = "221846a5-866d-43ef-bb19-6883fe1c2bdb"


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


def headers() -> dict[str, str]:
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
        f"https://api.notion.com/v1{path}",
        data=data,
        headers=headers(),
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"Notion {method} {path} failed HTTP {exc.code}: {body[:1200]}") from exc


def select_options(names: list[str], color: str = "default") -> dict:
    return {"select": {"options": [{"name": name, "color": color} for name in names]}}


def multi_select_options(names: list[str], color: str = "default") -> dict:
    return {"multi_select": {"options": [{"name": name, "color": color} for name in names]}}


# Notion property definitions for reusable creator CRM + campaign lifecycle memory.
PROPERTY_DEFS: dict[str, dict] = {
    # Workflow/lifecycle state, separate from the existing broad Status field.
    "Hashgifted Stage": select_options([
        "Applied", "Manual Review", "Shortlisted", "Outreach Sent", "Qualified",
        "Selected", "Content Posted", "Captured", "Complete", "Declined",
        "Ghosted", "Reserve", "Do Not Work With"
    ]),
    "Application Status": select_options([
        "New", "Reviewed", "Shortlisted", "Messaged", "Qualified", "Selected",
        "Not Selected", "Declined", "Completed"
    ]),
    "Decision": select_options(["Shortlist", "Manual Review", "Decline", "Reserve", "Selected", "Complete"]),
    "Decision Confidence": select_options(["High", "Medium", "Low"]),
    "Last Applied": {"date": {}},
    "Last Reviewed": {"date": {}},
    "Last Selected": {"date": {}},
    "Last Completed": {"date": {}},
    "Campaign Count": {"number": {"format": "number"}},
    "Selected Count": {"number": {"format": "number"}},
    "Completed Count": {"number": {"format": "number"}},
    "Creator Rating": {"number": {"format": "number"}},

    # Location/delivery eligibility.
    "Metro Area": select_options(["Melbourne", "Sydney", "Brisbane", "Other", "Unknown"]),
    "Metro Eligible": select_options(["Confirmed", "Likely", "Unconfirmed", "No"]),
    "Location Confidence": select_options(["Confirmed", "Likely", "Weak", "Unknown", "Outside"]),
    "Distance From Metro Km": {"number": {"format": "number"}},
    "Delivery Eligibility Notes": {"rich_text": {}},

    # Social/account metrics.
    "Followers": {"number": {"format": "number"}},
    "Engagement Rate": {"number": {"format": "percent"}},
    "Profile URL Source": {"url": {}},

    # Visual/media inspection fields captured from Instagram/TikTok/browser review.
    "Visual Review Status": select_options(["Not Reviewed", "Partial", "Reviewed", "Unavailable", "Needs Recheck"]),
    "Last Visual Review": {"date": {}},
    "Brand Fit": select_options(["Strong", "Good", "Maybe", "Weak", "Unsafe"]),
    "Content Quality": select_options(["Excellent", "Good", "Mixed", "Weak", "Unknown"]),
    "Reel Ability": select_options(["Strong", "Good", "Maybe", "Weak", "Unknown"]),
    "Audience Fit": select_options(["Strong", "Good", "Maybe", "Weak", "Unknown"]),
    "Engagement Quality": select_options(["Strong", "Good", "Thin", "Suspicious", "Unknown"]),
    "Brand Safety": select_options(["Clear", "Minor Concern", "Concern", "Unsafe", "Unknown"]),
    "Content Themes": multi_select_options([
        "Home", "Interiors", "Motherhood", "Family", "Food", "Hosting", "Lifestyle",
        "Beauty", "Fashion", "Wellness", "Events", "Bridal", "Flowers", "Gifting",
        "Travel", "Pets", "Fitness", "Gaming", "Comedy", "Business"
    ]),
    "Visual Style": multi_select_options([
        "Natural Light", "Neutral", "Warm", "Editorial", "Premium", "Colourful",
        "Minimal", "Cosy", "Clean", "Polished", "Casual UGC", "High Contrast",
        "Text Heavy", "Chaotic", "Product Spam"
    ]),
    "Visual Evidence": {"rich_text": {}},
    "Fit Signals": {"rich_text": {}},
    "Risk Notes": {"rich_text": {}},
}


def main() -> None:
    load_env()
    ds_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CREATORS_DS
    before = notion("GET", f"/data_sources/{ds_id}")
    existing = set((before.get("properties") or {}).keys())
    missing = {k: v for k, v in PROPERTY_DEFS.items() if k not in existing}
    if not missing:
        print(json.dumps({"data_source": ds_id, "added": [], "already_present": len(existing)}, indent=2))
        return
    # Add properties in one schema patch. Existing select options are not touched.
    notion("PATCH", f"/data_sources/{ds_id}", {"properties": missing})
    after = notion("GET", f"/data_sources/{ds_id}")
    after_props = set((after.get("properties") or {}).keys())
    still_missing = sorted(set(missing) - after_props)
    print(json.dumps({
        "data_source": ds_id,
        "added": sorted(k for k in missing if k in after_props),
        "still_missing": still_missing,
        "property_count_before": len(existing),
        "property_count_after": len(after_props),
    }, indent=2))
    if still_missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
