# Save campaign to the Notion designs store (email builder)

> When the user wants to load / reopen / continue editing a campaign in the
> live email builder at `https://my-email-builder.onrender.com/`, the
> campaign JSON **must be POSTed to the builder's designs endpoint**. A
> campaign sitting in `/tmp/<slug>-campaign.json` is invisible to the
> builder and invisible to the user. **Saving to designs is part of the
> deliverable**, not an optional cleanup.

## When this matters

- The user asks to "save", "store", "load", "open in the builder", or
  shows the builder URL after you've generated a campaign.
- The user has implicitly trusted that the campaign can be re-opened —
  i.e. you have produced something and handed it back. They expect to
  find it next time they open the builder.
- The user explicitly notes they cannot see the campaign in the builder
  (this is the strongest signal — fix the gap immediately).

## Endpoint

```
POST https://my-email-builder.onrender.com/api/designs
Content-Type: application/json
```

The builder's designs store is backed by a Notion DB
(`NOTION_TOKEN` + `NOTION_DESIGNS_DB` in the render env). On free tier
the POST is fast (<2s typically, can stretch to ~5s on cold start).

## Body shape — the full envelope

The endpoint accepts the full envelope in one POST. `name` at top
level, `campaign` nested as the complete campaign JSON. The metadata
fields exist so the design shows up correctly in the My Designs list
and so future searches/filters can use them.

```json
{
  "name": "More Stems + Glow Up Announcement",
  "objective": "value_prop",
  "campaignType": "broadcast",
  "audienceAwareness": "product_aware_to_value_aware",
  "primaryCTA": "see the new look",
  "subjectLine": "more flowers, a new look",
  "previewText": "a small change to how we send, and a quiet one to how we wrap.",
  "emotionalTone": "warm, quietly confident, no urgency, no discount framing",
  "approvalStatus": "draft",
  "componentsUsed": ["header", "heroes/hero-d-clay", "footer"],
  "sourceBriefLink": "telegram:/conversation/2026-06-05-stems-glowup",
  "klaviyoLink": "",
  "resultNotes": "Audience: RH | Newsletter (THh7qN). Exclude Welcome List 20% More Stems (Uk5tEa).",
  "campaign": {
    "campaignName": "More Stems + Glow Up Announcement",
    "subjectLine": "more flowers, a new look",
    "previewText": "a small change to how we send, and a quiet one to how we wrap.",
    "bodyBg": "#2c2825",
    "objective": "value_prop",
    "persona": "...",
    "lensRouting": "...",
    "awarenessState": "...",
    "blocks": [ ... ],
    "notes": "..."
  }
}
```

## What goes in `componentsUsed`

A flat list of every `component` name from the blocks, without
group prefixes (e.g. `"header"`, `"heroes/hero-d-clay"`,
`"sections/body-copy"`). The Notion record is searchable on this
field — keep it accurate.

## Reading back / verifying

After POST, the response body is the persisted record (with a new
`id`). Two ways to confirm it landed:

1. **Single record by id:**
   `GET https://my-email-builder.onrender.com/api/designs/<id>` —
   returns the full record including the nested `campaign` field.
2. **List endpoint:**
   `GET https://my-email-builder.onrender.com/api/designs` — returns
   `{"designs": [...]}`. The newest design sorts to the top of the
   list (no explicit `createdAt` filter, just look at the first row).

## Pitfall — campaign without metadata

If you POST just the `campaign` object (no `name`, no metadata), the
endpoint accepts it but the design shows up with `name: ""` in the My
Designs list and is unfindable by search. Always include the
envelope.

## Pitfall — `name` ≠ `campaignName`

The design's display name is the top-level `name`. The campaign's
internal name is `campaign.campaignName`. They can be the same string
or different. The user reads the `name` field in the My Designs list.

## Pitfall — re-saving updates the row

`POST /api/designs` creates a new record (new `id` each time). If you
want to update an existing design, use `PUT /api/designs/<id>` with
the same body shape. Don't POST the same campaign twice — you'll end
up with two rows in My Designs.

## End-to-end recipe (the pattern that worked for the
"more stems + glow up" campaign)

1. **Fetch live context** (with the brief as the search query):
   `GET /api/live-context?q=<brief>` → 4-source context (Shopify +
   Klaviyo + Shopify Atom blog + Asset Library).
2. **Author the campaign JSON** by hand (or via the LLM call if it's
   not timing out on Render free tier).
3. **Validate** with `POST /api/validate` → expect `{"ok": true}`.
4. **Assemble** with `POST /api/assemble` → expect HTML body, no
   unfilled tokens. This is a fast sanity check.
5. **Wrap in the metadata envelope** (name, objective, componentsUsed,
   etc.) and **POST to `/api/designs`**.
6. **Read back** via the list endpoint to confirm it landed; report
   the new design id to the user.
7. Tell the user the campaign name they'll see in My Designs; the
   builder URL is `https://my-email-builder.onrender.com/`.

## Why this matters — the user-facing reality

A campaign in `/tmp/` is invisible. A campaign in the designs store
is loadable from the builder UI, editable, re-renderable, and
exportable to Klaviyo. **The designs-store copy IS the deliverable**
for any campaign work. Don't hand back a file path and call it
done.
