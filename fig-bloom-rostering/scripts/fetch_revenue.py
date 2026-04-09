#!/usr/bin/env python3
"""
fetch_revenue.py
Fetch last 7 days gross revenue from Shopify and output weekly forecast + labour budget.

Usage:
    python fetch_revenue.py

Environment:
    SHOPIFY_STORE     - e.g. fig-and-bloom.myshopify.com
    SHOPIFY_TOKEN     - Admin API access token (shpat_...)

Output (JSON):
    {
        "period_start": "YYYY-MM-DD",
        "period_end":   "YYYY-MM-DD",
        "gross_revenue": 12345.67,
        "labour_budget": 1049.38,
        "labour_budget_pct": 0.085
    }
"""

import os, sys, json, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone

STORE = os.environ.get("SHOPIFY_STORE", "")
TOKEN = os.environ.get("SHOPIFY_TOKEN", "")
LABOUR_PCT = 0.085

if not STORE or not TOKEN:
    print(json.dumps({"error": "SHOPIFY_STORE and SHOPIFY_TOKEN env vars required"}), file=sys.stderr)
    sys.exit(1)

end = datetime.now(timezone.utc).date()
start = end - timedelta(days=7)

url = (
    f"https://{STORE}/admin/api/2024-01/orders.json"
    f"?status=any"
    f"&financial_status=paid"
    f"&created_at_min={start}T00:00:00Z"
    f"&created_at_max={end}T23:59:59Z"
    f"&fields=total_price"
    f"&limit=250"
)

headers = {
    "X-Shopify-Access-Token": TOKEN,
    "Content-Type": "application/json",
}

gross = 0.0
page_url = url

while page_url:
    req = urllib.request.Request(page_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            orders = data.get("orders", [])
            for o in orders:
                gross += float(o.get("total_price", 0) or 0)
            # Shopify cursor pagination via Link header
            link = resp.headers.get("Link", "")
            next_url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    next_url = part.strip().split(";")[0].strip().strip("<>")
            page_url = next_url
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"Shopify API error {e.code}: {e.reason}"}), file=sys.stderr)
        sys.exit(1)

result = {
    "period_start": str(start),
    "period_end": str(end),
    "gross_revenue": round(gross, 2),
    "labour_budget": round(gross * LABOUR_PCT, 2),
    "labour_budget_pct": LABOUR_PCT,
}

print(json.dumps(result, indent=2))
