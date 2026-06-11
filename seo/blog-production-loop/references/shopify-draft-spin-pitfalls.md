# Shopify draft spin pitfalls — Fig & Bloom blog production loop

Reusable lessons from running the loop against Fig & Bloom Shopify draft articles.

## Calendar rows may be schedule pointers, not source drafts

The editorial calendar data source can contain scheduling rows whose markdown body is only a pointer to the canonical Blog Posts page:

```md
➡️ **Draft lives in Blog Posts ▸ June** (single source of truth): <mention-page url="https://app.notion.com/p/..."/>
```

When this appears, follow the `mention-page` URL and read that page markdown before drafting or syncing to Shopify. Do not write from the scheduling row alone.

## New Notion API split: database container vs data source

For newer Notion databases, the `/v1/databases/{id}` response may be a container with `data_sources: [{id, name}]`. Query schema and rows via:

- `GET /v1/data_sources/{data_source_id}`
- `POST /v1/data_sources/{data_source_id}/query`

If `/v1/databases/{id}` shows zero properties but includes `data_sources`, switch to the data source ID.

## Draft-only Shopify critic mode

Shopify draft articles may not have a public preview URL available to the agent. For draft-only runs, do not publish just to make the critic possible. The critic may judge from Shopify read-back HTML and metadata, with this limitation stated in the run report.

Minimum read-back checks before critic:

- `isPublished == false`
- title and handle match
- summary length > 0
- body length plausible
- article image present
- inline images present where expected
- no duplicate title heading in body
- no banned-language hits
- no public scaffolding (`CTA:`, placeholders, prompt residue, internal notes)

## Markdown-to-HTML conversion hazards

Notion markdown often escapes bullets or flattens metadata. A naive converter can create hard-gate render defects even when local text QA looks clean.

Check specifically for:

- literal hyphen inside list items: regex like `<li>\s*-\s*`
- product callout nested inside a still-open `<ul>`
- public `CTA:` lines leaked from source metadata
- first article title repeated as the first H2
- meta-description text captured into a slug/handle because metadata was flattened onto one line

Product callouts should be inserted outside generated list markup. Safer default: append late in the body after markdown conversion, rather than inserting by raw line/chunk index.

## Product callout evidence for Guide-tier posts

Before asking the critic to pass a Guide, verify each body contains clear product-callout evidence:

- `blog-product-callout` block present
- real Shopify product image present
- product name present
- price text, e.g. `from $99.00`
- `Shop the [Product Name] →` link
- at least one commercial collection/product link
- at least one related editorial link where a relevant article exists

If no relevant related editorial article exists, report that limitation and compensate with stronger commercial/context links.

## Banned-language scan nuance

`blooms` as a noun is banned. Replace it broadly with `flowers` or a more specific term before upload. Do not only patch exact phrases like `beautiful blooms`.
