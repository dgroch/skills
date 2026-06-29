# Workspace Tree

Full hierarchy of the Notion workspace as of May 2026.

```
WORKSPACE ROOT
│
├── 🌸 Bower Brand OS (356fdc24-425f-8071-8dac-f93e052a19b3)
│   ├── 📄 🌿 Art Direction
│   ├── 📄 🎨 Colour System
│   ├── 📄 ✅ Critic Dimensions
│   ├── 📄 🧱 Grid Spec
│   ├── 📄 🧪 Prompt Construction
│   ├── 📄 ✍️ Voice & Copy
│   ├── 📄 🏷️ Logo & Assets
│   ├── 📊 👥 Characters (35efdc24...2fa2)
│   ├── 📊 💐 Products (35efdc24...9301)
│   ├── 📊 📍 Locations (35efdc24...d732)
│   └── 📊 📸 Shots (35efdc24...d5)
│
├── Brand — Whoosh (354fdc24-425f-802e-b6b1-f757a15cf4e0)
│   ├── 📄 Social Grid
│   ├── 📊 Characters (354fdc24...fd7f4)
│   ├── 📊 Locations (354fdc24...db67ba)
│   ├── 📊 Products (354fdc24...fd7f4)
│   └── 📊 Shots (83c4d220...d2f2)
│
├── Projects (366fdc24-425f-80ce-8151-c1b7dcf35b5a)
│   ├── 📄 Recipes & Pricing
│   ├── 📄 Style Bundle
│   ├── 📄 Bower
│   ├── 📄 Whoosh
│   ├── 📄 Moonpig
│   ├── 📄 Gift Cards (36afdc24...4164)
│   │   └── 📊 Gift Cards Register (36afdc24...cd71)
│   └── 📊 Projects (354fdc24...0222)
│
├── Systematic Portfolio (Beta) (369fdc24-425f-802b-8d83-c1f5e935174b)
│   ├── 📄 Investment Programme Explainer
│   ├── 📄 How to Operate the Portfolio System
│   ├── 📄 Throttled Leverage Strategy Candidate
│   ├── 📄 Reports & Performance Dashboard (36afdc24...6009)
│   │   ├── 📊 Summary Stats
│   │   ├── 📊 Equity Curve
│   │   ├── 📊 Monthly Returns
│   │   ├── 📊 Daily Returns
│   │   └── 📊 Holdings Snapshots
│   ├── 📄 Trade Execution Monitor (36afdc24...c3a44)
│   │   ├── 📊 Trade Executions
│   │   └── 📊 Rebalance Audits
│   └── 📄 Rebalance Calendar & Approvals (36afdc24...654762)
│       └── 📊 Scheduled Rebalances
│
└── [Fig & Bloom Main — parent 36dfdc24, partially inaccessible]
    │
    ├── Assets (352fdc24-425f-8088-930c-c5c1ff6afa95)
    │   ├── 📊 Manifest (357fdc24...665f) — 7,100+ items
    │   ├── 📊 Products (358fdc24...7ed5) — 425 items
    │   ├── 📊 Shots (358fdc24...dcf7)
    │   ├── 📊 Characters (53fa365a...dcc)
    │   └── 📄 Brand Photographer Backend (363fdc24...08c8a)
    │       └── 📊 Brand Photographer Artifacts (b1ecf2b1...d3d2)
    │
    ├── Advertising (361fdc24...partially accessible)
    │   └── Meta Ads Creative Framework (362fdc24...e106)
    │       ├── 📊 Social Media Ads (361fdc24...b339) — 45 items
    │       └── 📄 User Generated Content (35bfdc24...615ab9)
    │           ├── 📊 Campaigns (ab1819ee...09a3) — 5 items
    │           ├── 📊 Creators (b5e1059f...bc672) — 74 items
    │           └── 📊 Briefs (f0275d2e...e89a) — 6 items
    │
    ├── Creative Research (351fdc24...4e15c)
    │   ├── 📊 Fig & Bloom Creative Research (351fdc24...c365) — 99 items
    │   └── 📄 Comms Calendar — May/June 2026 Brief
    │
    ├── Product Research (351fdc24...0c9)
    │   ├── 📊 Oddly Viral Product Research (359fdc24...9d473) — 29 items
    │   └── 📄 Shortlist — 2026-04-30
    │
    └── Customer Research (357fdc24...c85c)
        └── 📊 Review Research — Raw Reviews (357fdc24...68f1) — 1,000+ items
```

## Data Flow Diagram

```
                    ┌─────────────┐
                    │  Raw Files  │
                    │ (Google Drive)│
                    └──────┬──────┘
                           │ vision manifest
                           ▼
                    ┌─────────────┐
                    │   Manifest  │◄── CDN upload
                    │  (7,100+)   │    (Cloudflare R2)
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Products │ │  Shots   │ │ Creative │
        │  (425)   │ │          │ │ Research │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Campaigns│ │Social    │ │ Review   │
        │   (5)    │ │Media Ads │ │ Research │
        └────┬─────┘ │  (45)    │ └──────────┘
             │       └──────────┘
             ▼
        ┌──────────┐     ┌──────────────┐
        │ Creators │     │  Scheduled   │
        │  (74)    │     │  Rebalances  │
        └──────────┘     └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Trade      │
                         │  Executions  │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Reports    │
                         │  & Dashboard │
                         └──────────────┘
```

## Brand OS Structure (Repeated per brand)

```
Brand Page
├── Identity & Position
├── Art Direction (photography principles, core scenes, avoid list)
├── Colour System (tokens, ratios, grading rules)
├── Critic Dimensions (quality rubric, pass/fail, hard rejects)
├── Grid Spec (social layout patterns)
├── Prompt Construction (AI image prompt recipes)
├── Voice & Copy (tone, pass/fail examples)
└── Seed Databases
    ├── Characters (people who appear in shots)
    ├── Locations (places shots happen)
    ├── Products (things being delivered/shown)
    └── Shots (reference images with CDN URLs)
```

This structure is identical for Bower and Whoosh. Fig & Bloom's brand OS is spread across the main workspace and the Assets section.
