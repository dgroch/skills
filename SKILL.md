---
name: skills
description: Collection of reusable OpenClaw agent skills.
---

# OpenClaw Skills

A curated set of agent skills for OpenClaw deployments.

## Available Skills

### deputy-connector
General-purpose connector for the Deputy staff rostering system API. Covers employee management, rostering, timesheets, locations, and the full Deputy Resource API.

**Requirements:** Deputy subdomain + API token (ask the user to provide these)

**Scripts:**
- `deputy_api_client.py` — generic API client with pagination support

### fig-bloom-rostering
Weekly staff roster builder for multi-location retail/service businesses. Forecasts labour budget from revenue data and constructs optimized rosters in Deputy respecting staff availability, employment type constraints, and leave.

**Requirements:** Deputy ( subdomain + token), Shopify (store + admin API token)

**Scripts:**
- `fetch_revenue.py` — pull last 7 days gross revenue from Shopify
- `fetch_roster_inputs.py` — pull employees and approved leave from Deputy

## Usage

Skills are loaded by the OpenClaw agent based on their `description` field. Trigger phrases include:
- Deputy: "roster", "rostering", "schedule", "shift", "timesheet", "leave", "employee"
- Revenue/labour: "labour budget", "forecast", "staff cost"

## Installing

Copy the skill directory to your agent's `skills/` folder, or use the ClawHub CLI:
```bash
clawhub install <skill-name>
```
