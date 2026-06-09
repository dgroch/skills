# Heartbeat — how the Conversion Intelligence loop is scheduled

The programme runs on a heartbeat, not a manual session. You confirmed the
runner will be a **Claude Code / Claude Cowork routine** rather than a dedicated
Paperclip VPS agent, so this doc covers that path first, with a plain-cron
fallback for a headless VPS.

## Cadence (confirmed)

| Cadence | Command | What it does |
|---|---|---|
| **Daily observe** | `python loop.py --mode daily` | 1-day window (yesterday). Refreshes funnel, ranks drop-off by revenue at risk, updates the hypothesis backlog, reads any live Mida tests, writes a Run Log row. |
| **Weekly readout** | `python loop.py --mode weekly` | 7-day window **with a pre/post compare** against the prior 7 days. Deeper read: trend deltas on each transition, test decisions (ship/kill), weekly Run Log row. |

Windows always end on **yesterday** (the last complete day) so partial-day data
never skews a read.

## Option A — Claude Code / Cowork routine (chosen)

Wire two recurring routines that invoke the loop. In Claude Code this is the
`/loop` capability or a scheduled task; in Cowork, a scheduled run. Each routine
just needs to:

1. `cd skills/conversion-intelligence`
2. ensure deps once: `pip install -r requirements.txt`
3. run the command for that cadence (table above)
4. surface the printed run summary; the durable record is the Notion Run Log.

Suggested schedule (store timezone, Australia/Sydney):
- Daily observe — every day ~07:00.
- Weekly readout — Mondays ~07:30 (after the daily has run).

The loop is headless-safe (no prompts) and fails soft, so a routine never hangs:
on a bad run it still writes a `Partial`/`Failed` Run Log row and exits non-zero
on hard failure (GA4 unreachable), which the routine can alert on.

## Option B — plain cron (headless VPS fallback)

```cron
# Conversion Intelligence Programme (timezone = store local, e.g. Australia/Sydney)
CRON_TZ=Australia/Sydney
0 7 * * *  cd /opt/skills/conversion-intelligence && /usr/bin/python3 loop.py --mode daily  >> /var/log/cro/daily.log 2>&1
30 7 * * 1 cd /opt/skills/conversion-intelligence && /usr/bin/python3 loop.py --mode weekly >> /var/log/cro/weekly.log 2>&1
```

## Pre-flight

Before enabling either schedule, run once interactively:

```bash
python loop.py --check          # validates creds + connectivity, no writes
python loop.py --mode daily --dry-run   # full compute, prints, writes nothing
python loop.py --mode daily     # real run; confirm a Run Log row appears in Notion
```

## Observability

There is no dashboard by design. The heartbeat's trail is the **CRO — Run Log**
database; every run appends one row (timestamp, window, top drop-off, actions,
records touched, status). A run that fails soft is still visible there as
`Partial` or `Failed` with the error captured in *Actions taken*.
