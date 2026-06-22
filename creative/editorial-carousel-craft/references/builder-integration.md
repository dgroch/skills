# Builder Integration

This skill does **not** render. Rendering, templates, fonts, ratios, asset sourcing, and
persistence are owned by the **`my-social-builder`** app and its companion writer skill
(`social-post-builder`, which emits the `post.json` the app renders). This skill is the
*editorial standard + critic* on top of that pipeline. Keep this file in sync with the
builder's `design-system/manifest.json` — if a lane's tokens change, update the lane map here.

## The pipeline (who does what)

```
social-post-builder  →  writes post.json for a lane
my-social-builder    →  renders the locked lane to a PNG set (Puppeteer, 2×)
editorial-carousel-craft (this skill)  →  picks the lane, holds the editorial bar,
                                          critiques the render, returns feedback
brand-guidelines-manager  →  source of truth for voice, palette, fonts
```

## Editorial lanes (from the builder manifest)

| Lane (`design`) | `lane` | Use for | Feed ratio |
|---|---|---|---|
| `carousel-journal` | journal | Multi-slide editorial carousel promoting a Journal post | 4:5 |
| `story-editorial` | editorial | Single editorial story frame | 9:16 |

Don't invent a lane. If a Journal carousel needs something no lane supports, that's a
**builder** change (add/extend a lane in `my-social-builder`), not an HTML file here.

## The interchange contract

`post.json` = `{ postName, design, ratio, slides:[{ slide, tokens }] }`. Tokens are
self-described in each template's `<!-- SLIDE … TOKENS: … -->` header and surfaced via the
app's `GET /api/schema`. Read the schema; never guess token names.

- **Photo tokens** accept `query: <describe the shot>`, resolved at render time against the
  Fig & Bloom Asset Library. **No AI photography**; no match → generate a plate via the
  brand-photographer route and upload to the library, then reference it.

## Fonts (facts — owned by the builder, do not redefine)

Lust (display) · **Cervanttis (italic — the real emphasis face)** · Neuzeit Grotesk
(Light body, Bold kicker/CTA). There is a genuine italic; **emphasis is Cervanttis italic,
used sparingly** — never a synthesised slant and never "Neuzeit-Bold-as-italic". If a lane
lacks an italic/emphasis token, that's a builder gap to raise, not a workaround to invent.

## API surface this skill uses

| Call | Purpose |
|---|---|
| `GET /api/schema` | Lanes, slides, tokens, levers, ratios — the contract |
| `GET /api/assets/search?q=…` | Resolve a photo token to a real plate |
| `POST /api/validate {post}` | Catch unknown/unfilled tokens before rendering |
| `POST /api/render {post, scale}` | Rasterise to a PNG set (scale 2 default) — what you critique |
| `POST /api/campaigns {name, posts[]}` | Submit a suite for human review |
| `GET /api/campaigns/:id` | Read back `posts[*].status` + `feedback[]` |
| `POST /api/campaigns/:id/posts/:postId/feedback {text}` | **Where this skill's critique goes** |
| `PUT /api/campaigns/:id/posts/:postId/post {post}` | Replace a post after editing (resets to pending) |

## The critique handoff

After the builder renders, run the seven-axis rubric (`references/critique-rubric.md`) on the
returned PNG set. Deliver the result as campaign feedback (`…/feedback`), not as a separate
document, so the build/review loop stays in one place. **Never publish — escalate to Dan.**
