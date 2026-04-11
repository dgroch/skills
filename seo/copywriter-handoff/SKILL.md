---
name: copywriter-handoff
description: Paperclip SEO workflow for Copywriter Handoff. Use this skill when you need to run structured work for Copywriter Handoff, including planning, monitoring, analysis, and execution handoffs.
---

# Copywriter Handoff (Paperclip)

This skill was adapted from the CSTMR SEO specialist system for Paperclip AI.

Paperclip path mapping:
- Treat any `tracker/` paths below as relative to your Paperclip project workspace data directory.
- Keep file structures and schemas consistent across runs so other SEO skills can consume outputs.
- Replace any references to `agent.yaml` routing with your Paperclip notification or orchestration settings.


## Purpose

Produce structured content briefs that the Copywriter agent can execute independently. This is the primary interface between Link (SEO) and the Copywriter agent. Brief quality directly determines content quality.

The full handoff contract (both sides) is defined in `AGENTS.md`.

## Tools Required

- Ahrefs (keyword data, competitor content analysis)
- SerpAPI (current SERP analysis, PAA, featured snippets)
- Firecrawl (competitor page content for reference)
- Google Search Console (current page performance for rewrites)

## Data Storage

- `tracker/briefs/{brief_id}.json` — individual brief files
- Status tracked in both the brief file and `tracker/state.json → tasks`

## Triggers

A brief is created when:
1. Content strategy identifies a gap or opportunity (`content-strategy` → `plan` or `review`)
2. On-page specs identifies a rewrite need (`on-page-specs` → `optimise`)
3. Keyword research surfaces a new content gap (`keyword-research` → `refresh`)
4. Seasonal calendar deadline approaching (`content-strategy` → `review`)
5. Underperforming content flagged for refresh (`analytics-reporting` → `weekly_summary`)
6. Operator requests specific content

## Brief Types

| Type | Description |
|------|-------------|
| `new_blog_post` | New informational/authority content |
| `new_landing_page` | New commercial/transactional page |
| `product_description` | New or revised product copy |
| `page_rewrite` | Full rewrite of underperforming page |
| `page_refresh` | Update existing page (new sections, updated data, improved structure) |
| `meta_copy` | Title tag and meta description updates only (simplified brief) |

## Brief Creation Steps

### Step 1 — SERP Research

1. SerpAPI: search target keyword with client's market params
2. Analyse top 5 ranking pages:
   - Title format, meta description approach
   - Heading structure (H1, H2s, H3s)
   - Content length (word count)
   - Content format (list, guide, comparison, story)
   - Topics covered
   - Media usage (images, video, tables, infographics)
   - Schema types
   - SERP features present (featured snippet format, PAA questions)

### Step 2 — Content Angle

1. What format works for this SERP? (match user expectation)
2. What topics do all/some/none of the top results cover?
3. What depth is expected?
4. What unique angle can the client bring? (expertise, local knowledge, product range, brand voice)

### Step 3 — Produce Brief

```json
{
  "brief_id": "brief-{NNN}",
  "type": "new_blog_post",
  "status": "handoff_copywriter",
  "created_at": "ISO8601",
  "created_by": "bloom",

  "target_keyword": {
    "keyword": "how to care for roses",
    "volume": 1200,
    "kd": 25,
    "intent": "informational",
    "current_position": null,
    "serp_features": ["featured_snippet", "paa", "images"]
  },
  "secondary_keywords": [
    { "keyword": "rose care tips", "volume": 800 },
    { "keyword": "how often to water roses", "volume": 600 }
  ],

  "page_spec": {
    "url_slug": "/blogs/care/how-to-care-for-roses",
    "title_tag": "How to Care for Roses — Complete Guide | {Brand}",
    "meta_description": "Learn how to care for roses...",
    "h1": "How to Care for Roses",
    "schema_type": "Article"
  },

  "content_spec": {
    "format": "comprehensive guide",
    "word_count_range": [1500, 2000],
    "suggested_headings": [
      "H2: Watering Your Roses",
      "H2: Pruning and Deadheading",
      "H2: Common Rose Problems",
      "H2: Seasonal Rose Care"
    ],
    "must_cover": [
      "Watering frequency by season",
      "Pruning technique and timing",
      "Pest and disease identification",
      "Feeding schedule"
    ],
    "unique_angle": "Australian climate focus, native companion planting",
    "featured_snippet_target": {
      "format": "paragraph",
      "question": "How often should you water roses?",
      "target_length": "40-60 words"
    },
    "paa_questions": [
      "How often should you water roses?",
      "When is the best time to prune roses?",
      "What is the best fertiliser for roses?"
    ],
    "media_suggestions": [
      "Hero image: healthy rose arrangement",
      "Inline: pruning technique diagram",
      "Inline: seasonal care calendar table"
    ]
  },

  "internal_links": {
    "link_to": ["/collections/roses", "/blogs/care/dried-flower-care"],
    "link_from": ["/collections/roses", "/blogs/care"]
  },

  "competitor_reference": [
    {
      "url": "https://example.com/rose-care-guide",
      "position": 1,
      "word_count": 2100,
      "strengths": "Comprehensive, well-structured, good images",
      "weaknesses": "Generic, not Australia-specific, no schema"
    }
  ],

  "tone_notes": "Warm but authoritative. Practical advice, not academic. Assume reader has roses already.",
  "audience": {
    "primary_segment": "self-care",
    "secondary_segment": "moment-makers",
    "reading_level": "general",
    "assumes_knowledge": "basic gardening"
  },
  "cta": {
    "primary": "Shop our rose collection",
    "secondary": "Subscribe for weekly flower care tips"
  },

  "deadline": "ISO8601",
  "priority": "medium",
  "context": "Part of flower care pillar cluster. No existing content on this topic."
}
```

### Step 4 — File and Track

1. Write brief to `tracker/briefs/{brief_id}.json`
2. Create task in state.json: type `brief`, status `handoff_copywriter`, linked to brief_id
3. If deadline is within 2 weeks, set priority to `high`

## Quality Checklist (Before Handoff)

- [ ] Target keyword validated (volume, KD, intent confirmed)
- [ ] SERP analysed (top 5 competitors reviewed)
- [ ] Heading structure is logical and covers must-have topics
- [ ] Word count range is realistic for the topic and SERP expectation
- [ ] Internal links are real, existing URLs (not guessed)
- [ ] Tone notes are specific to this piece (not generic)
- [ ] Featured snippet / PAA targets included where applicable
- [ ] Deadline allows sufficient time for writing + review
- [ ] No cannibalisation: no other page targets this keyword cluster
- [ ] URL slug follows platform conventions (`config/client.yaml → shopify.url_structure`)

## Review Process (Post-Copywriter)

When Copywriter sets brief status to `copy_review`:

1. **SEO alignment check:**
   - Title tag matches spec (keyword, length, brand)
   - Meta description matches spec (keyword, length, CTA)
   - H1 matches spec
   - Heading structure follows suggested outline
   - Target keyword appears naturally in first 100 words, headings, and throughout
   - Internal links are present and correct
   - Word count within specified range
   - Featured snippet section is formatted correctly (if targeted)
   - FAQ/PAA section present (if specified)
2. **Quality check:**
   - Content matches search intent
   - Unique angle is present (not a generic rehash)
   - Tone matches client brand
   - No keyword stuffing
   - Reads naturally
   - CTA is present
3. **Result:**
   - Pass → status `approved`, task `completed`
   - Fail → status `revision_needed`, `revision_notes` array with specific issues

## Meta Copy Briefs

Simplified format for title tag and meta description updates only:

```json
{
  "brief_id": "brief-{NNN}",
  "type": "meta_copy",
  "status": "handoff_copywriter",
  "url": "/collections/example",
  "target_keyword": "...",
  "title_tag_spec": "format + example",
  "meta_description_spec": "format + example",
  "notes": "why this change is needed"
}
```
