# Conversion Intelligence Programme

A closed CRO learning loop for **Fig & Bloom** (`figandbloom.com.au`):

> **Observe → Hypothesise → Test → Read → Decide + Log → repeat**

It reads behavioural + commerce data, finds friction and drop-off, proposes
prioritised experiments, reads experiment results, and logs every step to Notion
so the loop is observable and compounds over time. It runs **headless on a
heartbeat**, talking to vendor APIs directly (no desktop/npx MCP servers).

It does **not** ingest raw session recordings — events and metrics only.

## What it does each run

1. **Observe** — GA4 funnel + Shopify outcomes (orders, AOV, abandoned checkouts) for the window.
2. **Detect** — rank drop-off points by **lost-revenue impact**, not just CVR.
3. **Hypothesise** — refresh a ranked, ICE-scored backlog; write new hypotheses to Notion.
4. **Read tests** — pull live Mida experiment results; mark significant / ship / kill.
5. **Decide + Log** — write decisions and a run summary to the Notion Run Log.

## Architecture

| Layer | Source | Client | Access |
|---|---|---|---|
| Outcome truth | Shopify | `clients/shopify.py` | Admin GraphQL API (token) |
| Behavioural funnel | GA4 | `clients/ga4.py` | GA4 Data API, **read-only** (service account) |
| Causal / experiments | Mida.so | `clients/mida.py` | Mida V2 reporting API, GA4-bridge fallback |
| Ledger / observability | Notion | `clients/notion_ledger.py` | Notion REST API (integration token) |

The funnel is **locked** in `funnel.py` and measured the same way every run:

```
Collection/Home → Product (bouquet) → Add to cart → Checkout started → Purchase
       (view_item_list) → (view_item) → (add_to_cart) → (begin_checkout) → (purchase)
```

## Layout

```
conversion-intelligence/
├── SKILL.md            # the OpenClaw skill (decision tree, gates, failure modes, tacit knowledge)
├── README.md           # this file
├── requirements.txt
├── funnel.py           # locked funnel definition (single source of truth)
├── playbook.py         # tacit knowledge: transition → candidate hypothesis + ICE priors
├── loop.py             # OODA orchestrator — what the heartbeat calls
├── clients/
│   ├── ga4.py
│   ├── shopify.py
│   ├── mida.py
│   └── notion_ledger.py
├── config/
│   ├── .env.example    # every secret, documented
│   └── .env            # local only, gitignored
└── cron/heartbeat.md   # scheduling (Claude Code/Cowork routine + cron fallback)
```

## Setup

```bash
cd skills/conversion-intelligence
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config/.env.example config/.env   # then fill in secrets
```

### Secrets (`config/.env`)

See `config/.env.example` for the full, documented list. You need:

- **GA4**: `GA4_PROPERTY_ID` (numeric) + `GA4_SERVICE_ACCOUNT_JSON` (path or raw JSON). The service account needs **Viewer** on the GA4 property.
- **Shopify**: `SHOPIFY_STORE` (`lechoixflowers.myshopify.com`) + `SHOPIFY_ADMIN_TOKEN` (read scopes: `read_orders`, `read_checkouts`).
- **Mida**: `MIDA_PROJECT_KEY` + `MIDA_API_KEY` (+ `MIDA_API_BASE` region). If you don't use the reporting API, leave these blank and set `MIDA_BRIDGE_TESTS` to read results via the GA4 bridge instead.
- **Notion**: `NOTION_TOKEN` (internal integration) + the three DB ids (already pre-filled — see below).

### Notion ledger (already created)

The three databases exist under the **CRO — Conversion Intelligence Programme**
page and their ids are pre-filled in `config/.env`:

| Database | ID |
|---|---|
| CRO — Hypotheses | `873a3600a88b47428934ef6f5cce3333` |
| CRO — Tests | `b6118f3b0c774bffa81f17fdfb1fa8f5` |
| CRO — Run Log | `9c48b09cab984ae1b0fdeee5c55c2416` |

> **One-time step:** share the parent page with your Notion **integration**
> (the one behind `NOTION_TOKEN`). The databases were created via a workspace
> connection; the headless integration token needs its own access. In Notion:
> open the parent page → `•••` → *Connections* → add your integration.

## Run it

```bash
# 1. Validate config + connectivity (read-only, no writes)
python loop.py --check

# 2. Full compute, print everything, write nothing
python loop.py --mode daily --dry-run

# 3. Real daily run (writes to Notion)
python loop.py --mode daily

# Weekly deep readout (7-day window + pre/post compare)
python loop.py --mode weekly

# Arbitrary window
python loop.py --mode manual --window-days 14
```

Windows end on **yesterday** (last complete day). A run always writes exactly
one **Run Log** row — `OK`, `Partial`, or `Failed` — even when a stage errors,
because the loop fails soft.

## How the heartbeat runs it

See [`cron/heartbeat.md`](cron/heartbeat.md). In short: a Claude Code / Cowork
routine runs `--mode daily` every morning and `--mode weekly` on Mondays. A
plain-cron snippet is provided as a VPS fallback.

## Design constraints

- **No raw recording ingestion** (Clarity stays out of v1).
- **Read-only on GA4** — never mutates analytics config.
- **Not a dashboard** — Notion is the surface.
- **Headless-safe** — no interactive prompts in `loop.py`; fail soft, log to Run Log.
- Respects API limits; paginates; degrades when a single source is unavailable.

## Phase 2 (scaffolded, not built)

A clean seam is left for a warehouse path: GA4 → BigQuery export and Shopify →
BigQuery for unlimited history and behaviour↔revenue joins. The clients return
plain dicts and the loop's detect/hypothesise stages take structured funnel +
outcome inputs, so a warehouse-backed reader can be swapped in behind the same
interfaces without touching the loop. Not implemented in Phase 1.
