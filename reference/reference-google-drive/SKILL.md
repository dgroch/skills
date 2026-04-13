```yaml
name: reference-google-drive
description: Conventions for interacting with Fig & Bloom Shared Drive.
author: Dan Groch
license: MIT
```

# Fig & Bloom Google Drive Conventions

Use this skill whenever you need to create, read, or organise files on Google Drive. It tells you where to put things and how to name them.

## Shared Drive

All company files live on the **Paperclip** shared drive.

- **Drive ID:** `0AFJ_DrnFD4bbUk9PVA`
- Always pass `"supportsAllDrives": true` in API params when using `gws drive` commands.
- Never store work files in personal My Drive.

## Department Folder Map

| Folder                | Drive Folder ID                     | Agents                                                                                                                                                                            |
| --------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01 - Executive        | `122374zeJDgMjOYnX-SJwhECHmoGDTXe8` | CEO                                                                                                                                                                               |
| 02 - Finance          | `1uyHsf2HVdt1iqNV3Dh6-zbu_2VtSKKyp` | FinanceManager                                                                                                                                                                    |
| 03 - Marketing        | `1wCqbXQCj5Fw3g-tEhTotg76bF6Dzon-T` | MarketingManager, ContentWriter, SocialMediaManager, BrandManager, EmailMarketingSpecialist, FacebookMediaBuyer, GoogleMediaBuyer, TikTokMediaBuyer, SEOSpecialist, CROSpecialist |
| 04 - Operations       | `1I2J1LS5_oUUnM_8TMix7fvOWYWKCgFeR` | OperationsManager, WorkforceManager, LogisticsManager, PurchasingManager                                                                                                          |
| 05 - Product          | `1cKKkjx2KCnvmrGYSaRETEwlvFzzz-BLf` | ProductResearcher                                                                                                                                                                 |
| 06 - Technology       | `1zQB_EKR55j66-mtKDSh-Q3kuTdpei-Xt` | ShopifyAdmin, ShopifyDeveloper                                                                                                                                                    |
| 07 - Customer Service | `14yNDEV5MhdYnvyNuAvSjAlVF5OQQSSuU` | CustomerServiceAgent                                                                                                                                                              |
| 08 - Data & Analytics | `11ATs4_36firpDH55bNXkq-OCUDTIREap` | DataAnalyst                                                                                                                                                                       |
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

## Naming Conventions

- Use clear, descriptive names. Lead with the topic, not the date.
- For dated files use `YYYY-MM-DD` format: `2026-04-12 Weekly Marketing Report`
- Use Google Docs version history instead of `v2`, `FINAL`, etc.
- Store reusable templates in `09 - Shared Resources > Templates`.

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
4. Do not change sharing/permission settings on individual files.
5. Archive old project folders with an `ARCHIVE -` prefix rather than deleting.
6. Do not leave files in the drive root.

## Full Documentation

See the [Google Drive Conventions & Usage Guide](https://docs.google.com/document/d/10ZxRf4TU8v5jYCkbL7P9iVZ1OM3PaCXHX5z3yhvULoE/edit) in the Shared Resources folder.
