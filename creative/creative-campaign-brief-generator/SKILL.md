---
name: creative-campaign-brief-generator
description: Generate a structured Markdown campaign brief for Fig & Bloom email campaigns. 
---

# Campaign Brief Generator — Fig & Bloom

This skill runs an interactive intake to produce a complete, structured Markdown brief that the downstream email builder skill can consume without further clarification.

The brief covers: occasion, goal, persona targeting, product selection (live Shopify fetch), offer details, key dates, sensitivity flags, accent colour, and tone direction.

**Reference files in `references/`:**
- `personas.md` — full persona definitions (read when selecting or describing target personas)
- `occasion-defaults.md` — pre-mapped defaults by occasion (read at the start of every intake)

---

## When to use this skill

Use this skill whenever someone wants to plan, brief, or kick off a Klaviyo email campaign — including seasonal campaigns (Mother's Day, Valentine's Day, Easter), promotional sends, subscription campaigns, gifting moments, or any ad-hoc email. Also triggers for phrases like "write a campaign brief", "set up a campaign for X", "plan our next email", "brief the email builder", "what do we need for the [occasion] campaign", or any request to prepare inputs for the email design pipeline. If a campaign is being discussed in any form, use this skill.

---

## Intake process

### Step 1 — Read defaults first

Before asking anything, read `references/occasion-defaults.md`. If the occasion is already known from context, pre-load the defaults silently and confirm them with the user rather than asking cold.

### Step 2 — Run the intake

Collect the fields below. Where a confident default exists (from `occasion-defaults.md` or clear contextual inference), apply it silently and surface it for confirmation — don't ask for information you can already infer.

Ask questions in natural conversational clusters, not as a form. Group related fields. Aim for 2–3 exchanges maximum before you have enough to produce a complete draft brief.

**Required fields:**

| Field | Notes |
|-------|-------|
| `occasion_theme` | The campaign hook. Could be seasonal, product launch, evergreen, promo. |
| `campaign_goal` | One primary goal: sales, subscriptions, awareness, retention, win-back. |
| `target_personas` | Primary + optional secondary. Read `personas.md` if uncertain. |
| `product_selection_method` | `shopify_fetch`, `manual`, or `hybrid` |
| `shopify_collection_handle` | Required if fetching. Default: full catalogue. |
| `curated_products` | Final shortlist after fetch/curation (3–6 products recommended). |
| `offer_details` | Promo code, discount %, free shipping, or "no offer." |
| `opt_out_required` | Boolean. See occasion defaults. Always ask to confirm if TRUE. |
| `delivery_cutoff_date` | Last date orders can be placed for on-time delivery. |
| `campaign_send_date` | Planned email send date. |
| `accent_colour` | Optional seasonal colour. HEX or descriptive (e.g. "blush / dusty rose"). |
| `tone_notes` | Any campaign-specific tone direction beyond brand defaults. |
| `special_instructions` | Anything else the email builder needs to know. |

**Inferencing rules:**
- If occasion = Mother's Day → `opt_out_required: true`, primary persona: Milestone Sender, secondary: Considered Giver, accent default: blush/soft pink
- If occasion = Valentine's Day → `opt_out_required: true` (relationship/loss sensitivity), primary: Milestone Sender + Considered Giver
- If occasion includes "sympathy" or "grief" → `opt_out_required: true`, tone: restrained and quiet, no offer
- If occasion = Christmas/end of year gifting → `opt_out_required: false` (confirm), primary: Considered Giver + Milestone Sender
- If occasion = Easter or seasonal/home → primary: Everyday Aesthete + Entertainer, `opt_out_required: false`
- If occasion = subscription promo or evergreen → primary: Everyday Aesthete, secondary: Trade Buyer, `opt_out_required: false`
- If occasion = birthday or general gifting → primary: Milestone Sender, `opt_out_required: false`

When `opt_out_required` would be TRUE, always surface this explicitly for human confirmation — don't silently set it. The stakes are real.

---

### Step 3 — Fetch Shopify products (if method is `shopify_fetch` or `hybrid`)

Fetch the live product catalogue using the web fetch tool:

**Full catalogue:**
```
https://lechoixflowers.myshopify.com/products.json
```

**Specific collection:**
```
https://lechoixflowers.myshopify.com/collections/[handle]/products.json
```

From the JSON response, extract for each product:
- `title`
- `handle`
- `variants[0].price`
- First image URL (`images[0].src`)
- `product_type` and `tags`

Filter to products relevant to the campaign occasion and persona. Curate to a shortlist of 3–6 products. If the campaign has a hero product, flag it.

If the fetch fails or returns empty, fall back to manual product entry — ask the user to name the key products.

---

### Step 4 — Draft the brief

Once all fields are collected, produce the brief using the template below. Do not add preamble or commentary — output the brief directly.

---

## Brief output template

```markdown
# Campaign Brief — [Occasion/Theme]
**Date generated:** [today's date]
**Status:** Draft — pending review

---

## Campaign overview

| Field | Value |
|-------|-------|
| Occasion / theme | [value] |
| Campaign goal | [value] |
| Send date | [value] |
| Delivery cutoff | [value] |

---

## Audience

**Primary persona:** [Persona name]
> [1-sentence persona summary from personas.md]

**Secondary persona:** [Persona name or "None"]
> [1-sentence summary if applicable]

**Opt-out segment required:** [Yes / No]
[If Yes: "Include opt-out link for customers who have flagged sensitivity to [occasion] messaging."]

---

## Products

**Selection method:** [Shopify fetch / Manual / Hybrid]
**Collection:** [handle or "Full catalogue"]

| Product | Handle | Price | Notes |
|---------|--------|-------|-------|
| [name] | [handle] | $[price] | [Hero / Supporting / Optional] |
| ... | | | |

[If hero product exists: "**Hero product:** [name] — [brief reason why it leads]"]

---

## Offer

**Promo active:** [Yes / No]
[If Yes:]
- Type: [% discount / free shipping / bundle / gift with purchase]
- Code: [CODE]
- Conditions: [e.g. min spend, expiry, exclusions]

[If No: "No promotional offer. Campaign is editorial/awareness-led."]

---

## Creative direction

**Accent colour:** [HEX or descriptive, or "brand defaults only"]
**Tone notes:** [Any campaign-specific direction]

Brand voice reminder: warm, editorial, minimal, premium, Australian English. Avoid: "elevate," "curate," "stunning," "gorgeous," "pop of colour."

---

## Special instructions

[Free text, or "None."]

---

## Downstream handoff

This brief is ready for the **email builder skill**. Inputs confirmed: ✓ occasion ✓ personas ✓ products ✓ offer ✓ dates ✓ opt-out flag
```

---

## Quality gates before output

Before producing the final brief, verify:
- [ ] `opt_out_required` has been explicitly confirmed by the user if TRUE
- [ ] At least 3 products are in the curated list (or reason noted if fewer)
- [ ] `delivery_cutoff_date` is present — this is non-negotiable for the email builder
- [ ] Persona selection is coherent with the occasion
- [ ] No brand voice violations in tone notes (check: elevate, curate, stunning, gorgeous, pop of colour)

If any gate fails, ask the one missing question before outputting.

---

## After output

Offer two next actions:
1. "Ready to pass to the email builder skill — confirm when you'd like to proceed."
2. "Want to adjust anything in the brief before handoff?"

Do not ask both as questions simultaneously — present them as options.
