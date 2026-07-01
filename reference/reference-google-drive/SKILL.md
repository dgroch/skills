---
name: reference-google-drive
description: Conventions for creating, reading, naming, organising, and routing Fig & Bloom work files in the Paperclip shared Google Drive. Use when storing deliverables, choosing Drive folders, creating Docs/Sheets/Slides, archiving project outputs, or deciding where agent work products belong.
---

# Fig & Bloom Google Drive Conventions

Use this skill whenever you need to create, read, or organise files on Google Drive. It tells you where to put work, how to name it, and how to route agent outputs so files stay discoverable, reusable, and easy to hand off.

## Shared Drive

All company work files belong in the **Paperclip** shared drive.

- **Drive ID:** `0AFJ_DrnFD4bbUk9PVA`
- Always pass `"supportsAllDrives": true` in API params when using `gws drive` commands.
- Never store operating documents in personal My Drive folders.
- Do not leave files in the shared-drive root.

## Department Folder Map

| Folder                | Drive Folder ID                     | Agents                                                                                                                                                                            |
| --------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01 - Executive        | `122374zeJDgMjOYnX-SJwhECHmoGDTXe8` | CEO, ChiefOfStaff                                                                                                                                                                |
| 02 - Finance          | `1uyHsf2HVdt1iqNV3Dh6-zbu_2VtSKKyp` | FinanceManager                                                                                                                                                                    |
| 03 - Marketing        | `1wCqbXQCj5Fw3g-tEhTotg76bF6Dzon-T` | MarketingManager, ContentWriter, SocialMediaManager, BrandManager, EmailMarketingSpecialist, FacebookMediaBuyer, GoogleMediaBuyer, TikTokMediaBuyer, SEOSpecialist, CROSpecialist, PRSpecialist, PartnershipsManager |
| 04 - Operations       | `1I2J1LS5_oUUnM_8TMix7fvOWYWKCgFeR` | OperationsManager, WorkforceManager, LogisticsManager, PurchasingManager, TrainingDev                                                                                            |
| 05 - Product          | `1cKKkjx2KCnvmrGYSaRETEwlvFzzz-BLf` | ProductResearcher                                                                                                                                                                 |
| 06 - Technology       | `1zQB_EKR55j66-mtKDSh-Q3kuTdpei-Xt` | ShopifyAdmin, ShopifyDeveloper, UX/UI, engineering                                                                                                                                |
| 07 - Customer Service | `14yNDEV5MhdYnvyNuAvSjAlVF5OQQSSuU` | CustomerServiceAgent                                                                                                                                                              |
| 08 - Data & Analytics | `11ATs4_36firpDH55bNXkq-OCUDTIREap` | DataAnalyst, Research Analyst                                                                                                                                                     |
| 09 - Shared Resources | `1NT15AiujwHllLu0dlr2Exy_BGD88kErJ` | Everyone (cross-team work)                                                                                                                                                        |

## Sub-folders

### 01 - Executive

- Strategy & Planning
- Board & Reporting
- Company Policies

### 02 - Finance

- Budgets & Forecasts
- Reports
- Invoices & Expenses

### 03 - Marketing

- Campaigns
- Content
- Brand Assets
- Social Media
- Email Marketing
- SEO
- Paid Media
- CRO
- Partnerships
- PR

### 04 - Operations

- Workforce & Rostering
- Logistics & Shipping
- Purchasing & Suppliers
- SOPs & Procedures

### 05 - Product

- Research
- Product Briefs

### 06 - Technology

- Shopify
- Integrations
- Technical Docs

### 07 - Customer Service

- Playbooks & Scripts
- Escalation Logs
- Customer Feedback

### 08 - Data & Analytics

- Dashboards
- Reports
- Data Sources

### 09 - Shared Resources

- Templates
- Meeting Notes
- Cross-Team Projects

## Role Routing Notes

- Chief of Staff work defaults to `01 - Executive` unless it is a reusable cross-team asset.
- Training and onboarding playbooks default to `04 - Operations > SOPs & Procedures`.
- Reusable templates belong in `09 - Shared Resources > Templates`.
- Partnerships work belongs in `03 - Marketing > Partnerships`.
- PR work belongs in `03 - Marketing > PR`.
- Research Analyst outputs default to `08 - Data & Analytics > Reports` unless they are tightly product-specific; product-specific research belongs in `05 - Product > Research`.
- UX / UI design outputs default to `06 - Technology > Technical Docs` unless they are shared delivery assets for multiple teams.

## Naming Conventions

- Use clear, descriptive names. Lead with the topic, not the date.
- For dated files use `YYYY-MM-DD` format: `2026-04-12 Weekly Marketing Report`.
- Use Google Docs version history instead of `v2`, `FINAL`, `final-final`, or similar names.
- Store reusable templates in `09 - Shared Resources > Templates`.
- Time-stamped run folders must live inside the relevant campaign or project folder, not directly under a department root.
- Cross-team project outputs should use `09 - Shared Resources > Cross-Team Projects > <Project or Brand> > Outputs > FIGA-####` where possible.

## File Types

Use Google Workspace native formats:

- **Google Docs** for written documents, SOPs, briefs
- **Google Sheets** for data, budgets, trackers
- **Google Slides** for presentations, pitch decks

## Creating Files (Quick Reference)

```bash
# Create a file in your department folder
gws drive files create \
  --json '{"name": "My Document", "mimeType": "application/vnd.google-apps.document", "parents": ["<FOLDER_ID>"]}' \
  --params '{"fields": "id,name,webViewLink", "supportsAllDrives": true}'
```

MIME types:

- Folder: `application/vnd.google-apps.folder`
- Doc: `application/vnd.google-apps.document`
- Sheet: `application/vnd.google-apps.spreadsheet`
- Slides: `application/vnd.google-apps.presentation`

## Rules

1. Always use the Paperclip shared drive, never My Drive.
2. Store files in your department folder or the most specific sub-folder.
3. Use `09 - Shared Resources` for cross-team deliverables.
4. Do not change sharing/permission settings on individual files unless a task explicitly requires it.
5. Archive old project folders with an `ARCHIVE -` prefix rather than deleting.
6. Do not leave files in the drive root.

## Review Notes

- April 2026 directory review: the existing nine top-level folders still fit the org; no new top-level department folder is required.
- June 2026 directory review: the nine top-level folders still fit the current org. Added `03 - Marketing > PR` for PRSpecialist work and kept `03 - Marketing > Partnerships` for PartnershipsManager work. Research Analyst outputs route to `08 - Data & Analytics > Reports` unless product-specific. Archived stale April 2026 generated campaign-draft run folders with `ARCHIVE -` prefixes; no files were deleted. Continue using `09 - Shared Resources > Cross-Team Projects` for multi-team delivery outputs.

## Full Documentation

See the [Google Drive Conventions & Usage Guide](https://docs.google.com/document/d/10ZxRf4TU8v5jYCkbL7P9iVZ1OM3PaCXHX5z3yhvULoE/edit) in the Shared Resources folder.
