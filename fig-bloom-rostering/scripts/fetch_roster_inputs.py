#!/usr/bin/env python3
"""
fetch_roster_inputs.py
Fetch everything needed to build the roster from Deputy:
  - All employees with type, pay rate, min hours, availability
  - Any leave approved for the target week

Usage:
    python fetch_roster_inputs.py [YYYY-MM-DD]
    (date = start of the roster week; defaults to next Monday)

Environment:
    DEPUTY_SUBDOMAIN  - e.g. figandbloom.au.deputy.com
    DEPUTY_TOKEN      - Permanent API token

Output (JSON):
    {
      "week_start": "YYYY-MM-DD",
      "week_end":   "YYYY-MM-DD",
      "employees": [...],
      "leave": [...]
    }
"""

import os, sys, json, urllib.request, urllib.error
from datetime import datetime, timedelta, date

SUBDOMAIN = os.environ.get("DEPUTY_SUBDOMAIN", "")
TOKEN = os.environ.get("DEPUTY_TOKEN", "")

if not SUBDOMAIN or not TOKEN:
    print(json.dumps({"error": "DEPUTY_SUBDOMAIN and DEPUTY_TOKEN env vars required"}), file=sys.stderr)
    sys.exit(1)

BASE = f"https://{SUBDOMAIN}/api/v1"
HEADERS = {
    "Authorization": f"DeputyKey {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Determine week
if len(sys.argv) > 1:
    week_start = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
else:
    today = date.today()
    week_start = today + timedelta(days=(7 - today.weekday()))  # next Monday

week_end = week_start + timedelta(days=6)


def deputy_get(endpoint):
    url = f"{BASE}/{endpoint}"
    results = []
    start = 0
    while True:
        paged = f"{url}?start={start}&limit=500"
        req = urllib.request.Request(paged, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                if not data:
                    break
                results.extend(data if isinstance(data, list) else [data])
                if len(data) < 500:
                    break
                start += 500
        except urllib.error.HTTPError as e:
            print(json.dumps({"error": f"Deputy API error {e.code} on {endpoint}: {e.reason}"}), file=sys.stderr)
            sys.exit(1)
    return results


employees_raw = deputy_get("resource/Employee")
employees = []
for emp in employees_raw:
    if emp.get("Active") is False:
        continue
    employees.append({
        "id": emp.get("Id"),
        "name": f"{emp.get('FirstName', '')} {emp.get('LastName', '')}".strip(),
        "employment_type": emp.get("EmploymentTypeId"),  # 1=FT, 2=PT, 3=Casual
        "company_id": emp.get("Company"),
    })

# Fetch leave for the week
leave_raw = deputy_get(
    f"resource/Leave?search={{\"strDateStart\":\"gte:{week_start}\",\"strDateEnd\":\"lte:{week_end}\",\"intStatus\":1}}"
)
leave = [
    {
        "employee_id": l.get("Employee"),
        "start": l.get("DateStart"),
        "end": l.get("DateEnd"),
        "type": l.get("TypeId"),
    }
    for l in leave_raw
]

output = {
    "week_start": str(week_start),
    "week_end": str(week_end),
    "employees": employees,
    "leave": leave,
}

print(json.dumps(output, indent=2))
