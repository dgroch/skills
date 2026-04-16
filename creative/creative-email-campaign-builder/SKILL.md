---
name: creative-email-campaign-builder
description: Build complete Klaviyo email campaigns for Fig & Bloom using the v4 template library. Use this skill whenever someone asks to create an email campaign, email design, Klaviyo email, marketing email, promotional email, newsletter, or EDM for Fig & Bloom.
---

# Email Campaign Builder — Fig & Bloom (v4)

Builds production-ready Klaviyo emails by assembling pre-built, locked templates. The agent selects components and injects content. It does not write HTML or make design decisions.

## Core principle

**The agent is a content editor, not a designer or developer.**

Every layout decision, style rule, illustration, icon, and colour is already baked into the template files. The agent's only job is:
1. Select the right templates for this campaign
2. Write good copy for the token values
3. Assemble and validate

---

## Pipeline

```
1. BRIEF         → Campaign parameters
2. PRODUCTS      → Fetch from Shopify, select 3–5
3. COPY          → Write all token values (headlines, body, CTAs)
4. SELECT        → Choose components from references/manifest.json
5. RENDER        → Fill tokens into templates → slice visual components to PNG via puppeteer skill
6. VALIDATE      → Check all tokens filled, all slices produced, pre-flight checks
7. PREVIEW       → Assemble preview email (slices + HTML text blocks). Save to Google Drive only. Wait for approval.
8. UPLOAD        → Upload approved slices to Klaviyo media library. Get hosted URLs.
9. PRODUCTION    → Assemble final email HTML (Klaviyo slice URLs + text block HTML)
10. KLAVIYO      → Upload template + create campaign. Wait for approval before scheduling.
```

**Every numbered step is a gate. Do not skip ahead.**

**Dependency:** This skill requires the `puppeteer` skill to be installed and configured on the VPS. Verify with `node -e "require('puppeteer'); console.log('OK')"` before first use.

---

## Google Workspace Credentials

All Google Drive operations in this skill use the **`$GWS_USER_ADMIN`** credential (admin@figandbloom.com.au). This account has access to the Paperclip shared drive and all Marketing department folders.

**Important:** The `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` env var is set globally and takes precedence over `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`. Always unset it when using a profile-based config:

```bash
env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
  GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_ADMIN \
  gws drive ...
```

Use this pattern for every `gws drive` command in Steps 7 and 9.

---

## Step 1: Campaign Brief

Collect or parse:
```
Campaign name, goal, audience, tone, products (Shopify collection URL),
promo code (if any), opt-out required (yes/no), delivery cutoffs, accent colour (if any)
```

Auto-infer opt-out requirement:
- **Required:** Mother's Day, Father's Day, Valentine's Day/Galentine's, pregnancy/baby, memorial
- **Not required:** seasonal, product launch, general promo, retention

---

## Step 2: Product Selection

Read `references/product-selection.md` before fetching.

Fetch the Shopify collection. Select 3–5 products optimising for price spread, visual variety, and type mix. Assign card layout per product:
- Hero/spotlight product → `card-lifestyle-studio` (one per email max)
- Equal-weight products → `card-horizontal` + `card-horizontal-reversed` (alternating)
- Product with strong review → `card-single-testimonial`

Present selection with rationale. Wait for approval.

---

## Step 3: Copy (Token Values)

Read `references/brand-voice.md` before writing any copy.

Write values for every token that will be used. Key rules:
- `HEADLINE` case **depends on the font used in the selected template** — check the template comment block:
  - **Cervanttis templates** (hero-a, hero-b, hero-c, hero-d, upsell-noir, opt-out) → **MUST be lowercase**. e.g. `"for the one who does it all"`
  - **Lust templates** (body-copy, section-headline, all product cards) → **Sentence case**. e.g. `"Some gestures speak before words do."`
- `OPT_OUT_HEADLINE` → always lowercase (Cervanttis)
- `UNSUBSCRIBE_URL` token value → `{{ unsubscribe_url }}` (single braces, spaces inside — exact Klaviyo syntax)
- `REVIEW_STARS` → use Unicode star characters: `★★★★★`
- `BODY_P2` → empty string `""` if only one paragraph needed

---

## Step 4: Component Selection

Read `references/manifest.json` to confirm component file paths and token names.

Standard component order:

```
header                       ← always first
hero (choose one variant)    ← always
opt-out                      ← if required (immediately after hero)
body-copy
divider (optional — max 1 non-line divider per email)
section-headline
products (1–5 cards, mixed types)
testimonial                  ← if review copy available
promo-code                   ← if campaign has offer
upsell-noir                  ← closing beat
delivery-cutoffs             ← if hard deadline
trust-bar                    ← always
footer                       ← always last
```

**Hero selection guide:**

| Variant | When to use |
|---|---|
| `hero-a` | Standard campaigns. Maximum photo impact. |
| `hero-b-white/clay/noir` | Photo must be seen unobscured. Editorial feel. |
| `hero-c1` / `hero-c2` × `white/clay/noir` | Portrait photography. Most editorial. |
| `hero-d-noir` | Launches, VIP, re-engagement. Maximum brand statement. |
| `hero-d-clay` / `hero-d-white` | Type-forward but warmer tone. |

---

## Step 5: Render (token injection + slicing)

This step fills tokens into templates and renders visual components as PNG slices using the `puppeteer` skill.

### 5a. Classify components

Divide the selected component list into two groups:

**Slice to PNG** (visual — render via Puppeteer):
- header, all hero variants, all product cards, body-copy (illustrated variant), testimonial, upsell-noir, trust-bar, divider-illo-*

**Keep as HTML** (text-only — safe in all email clients, stays selectable/responsive):
- opt-out, section-headline, delivery-cutoffs, footer, body-copy-plain, divider-line, divider-whitespace

**Body-copy variant selection:**
- `body-copy` (sliced) — includes the HandRose accent illustration (bottom-right, 10% opacity). Use when you want the illustration.
- `body-copy-plain` (HTML) — no illustration, pure typography. **Prefer this by default** — text stays selectable, accessible, and responsive in email clients.

### 5b. Pre-download product images

Shopify CDN URLs are flaky when fetched concurrently during slicing. **Pre-flight each URL then download every image before rendering.** Use local `file://` paths in token values for all `{{PRODUCT_IMAGE_URL}}`, `{{LIFESTYLE_IMAGE_URL}}`, and `{{STUDIO_IMAGE_URL}}` tokens.

#### Preflight: validate image URLs before downloading

For every product image URL, confirm it resolves to an actual image before attempting the full download:

```bash
# Check Content-Type header — must start with "image/"
CONTENT_TYPE=$(curl -sI --max-time 10 "[shopify-url]" | grep -i '^content-type:' | awk '{print $2}' | tr -d '\r')
if [[ "$CONTENT_TYPE" != image/* ]]; then
  echo "ERROR: URL does not resolve to an image (got: $CONTENT_TYPE) — [shopify-url]"
  # Use fallback URL or abort
fi
```

If a URL fails preflight:
1. Try the product's alternate image URL (next variant or `.jpg` format swap).
2. If no alternate is available, flag the product and remove it from the campaign — **do not proceed with a broken image URL**.

#### Download with MIME and byte-size checks

```bash
mkdir -p /tmp/[campaign-slug]/product-images

download_image() {
  local url="$1"
  local dest="$2"
  local min_bytes=5000   # reject files smaller than 5KB as likely error pages

  # Up to 3 attempts with exponential back-off
  for attempt in 1 2 3; do
    curl -sL --max-time 30 "$url" -o "$dest"
    local status=$?
    if [ $status -ne 0 ]; then
      echo "  Attempt $attempt: curl error ($status) for $url"
      sleep $((attempt * 2))
      continue
    fi

    # Byte-size check
    local file_size
    file_size=$(wc -c < "$dest")
    if [ "$file_size" -lt "$min_bytes" ]; then
      echo "  Attempt $attempt: download too small (${file_size} bytes) — likely error page for $url"
      sleep $((attempt * 2))
      continue
    fi

    # MIME check on downloaded file
    local mime
    mime=$(file --mime-type -b "$dest")
    if [[ "$mime" != image/* ]]; then
      echo "  Attempt $attempt: downloaded file is not an image (MIME: $mime) for $url"
      sleep $((attempt * 2))
      continue
    fi

    echo "  ✓ Downloaded $dest (${file_size} bytes, $mime)"
    return 0
  done

  echo "ERROR: Failed to download valid image after 3 attempts: $url"
  return 1
}

# For each product image:
download_image "[shopify-url]" "/tmp/[campaign-slug]/product-images/[slug].jpg" || exit 1
```

After all downloads complete, verify none of the files are missing or zero-byte:

```bash
for f in /tmp/[campaign-slug]/product-images/*.jpg; do
  [ -s "$f" ] || { echo "ERROR: Empty or missing: $f"; exit 1; }
done
```

#### Use local file:// paths in tokens

Then in Step 5c token values, use `file://` paths instead of Shopify URLs:
- `{{PRODUCT_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug].jpg`
- `{{LIFESTYLE_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug]-lifestyle.jpg`
- `{{STUDIO_IMAGE_URL}}` = `file:///tmp/[campaign-slug]/product-images/[slug]-studio.jpg`

The product photos are baked into the slice PNGs during rendering — Step 8 uploads the composited slices to Klaviyo, so the original URLs aren't needed downstream.

### 5c. Prepare component HTML files

> **Note on template size:** Templates contain `{{ASSETS_BASE}}` tokens instead of base64 illustration data. This keeps each template file under 5KB so the agent can read them without context window pressure. The `slice.js` script resolves `{{ASSETS_BASE}}` to the absolute assets path at render time — the agent never handles image data directly.

For each **visual** component:
1. Read the template from `references/templates/[path].html`
2. Wrap it in `references/shell/shell-preview.html` (base64 fonts for correct Puppeteer render)
3. Replace every `{{TOKEN}}` with its value (product images use `file://` paths from 5b)
4. Verify no `{{` or `}}` remain
5. Save as a standalone HTML file in a working directory: `/tmp/[campaign-slug]/components/[name].html`

For each **text** component:
1. Read the template from `references/templates/[path].html`
2. Replace every `{{TOKEN}}` with its value
3. Verify no `{{` or `}}` remain
4. Hold in memory — these go directly into the final email HTML

### 5d. Slice visual components

Call the `puppeteer` skill's `slice.js` on the components directory. **Capture stdout to a file** so the `__SLICE_MANIFEST__` can be parsed in Step 6:

```bash
node [puppeteer-skill-path]/references/scripts/slice.js \
  --input /tmp/[campaign-slug]/components/ \
  --output /tmp/[campaign-slug]/slices/ \
  --assets [puppeteer-skill-path]/references/assets \
  --width 600 \
  --scale 2 \
  --verbose \
  | tee /tmp/[campaign-slug]/slice-output.txt
```

The `--assets` flag is required — it tells `slice.js` where to find the illustration PNG assets for `{{ASSETS_BASE}}` token substitution.

Parse the `__SLICE_MANIFEST__` from `/tmp/[campaign-slug]/slice-output.txt` to get the list of produced PNG files. The manifest includes a `broken_images` array per slice — if any entry is non-empty, the slice has failed image loads and must be re-rendered (check the `file://` path exists and the pre-download in 5b succeeded).

If any slice fails → fix the component HTML and re-run before proceeding.

---

## Step 6: Validation

**Slice validation:**
- [ ] `__SLICE_MANIFEST__` parsed — all expected PNG files are listed
- [ ] Every visual component has a corresponding PNG in `/tmp/[campaign-slug]/slices/`
- [ ] No slice errors in the Puppeteer output
- [ ] Every manifest entry has `broken_images: []` — any failures mean a pre-downloaded image is missing or `file://` path is wrong

**Product-grid aggregate check (mandatory):**

After parsing `__SLICE_MANIFEST__`, collect all product-card slice entries and verify the entire grid is clean — not just individual cards:

```bash
# Parse manifest and check all product card slices collectively
node -e "
const fs = require('fs');
const out = fs.readFileSync('/tmp/[campaign-slug]/slice-output.txt', 'utf8');
const match = out.match(/__SLICE_MANIFEST__([\s\S]*?)__END_MANIFEST__/);
if (!match) { console.error('No manifest found'); process.exit(1); }
const manifest = JSON.parse(match[1]);

const productSlices = manifest.slices.filter(s =>
  s.file.match(/card-|product-/i)
);
const gridBroken = productSlices.flatMap(s =>
  (s.broken_images || []).map(img => ({ slice: s.file, img }))
);

if (gridBroken.length > 0) {
  console.error('PRODUCT GRID BROKEN IMAGES:');
  gridBroken.forEach(b => console.error('  ' + b.slice + ': ' + b.img));
  process.exit(1);
}
console.log('Product grid OK — ' + productSlices.length + ' card(s), 0 broken images');
"
```

**Fail the build** if any broken-image indicator appears across the composed product grid. Do not proceed to Step 7 until all product card slices are clean.

If a card has broken images:
1. Confirm the corresponding `file://` path in the component HTML matches the pre-downloaded file.
2. Re-run the download for that image (Step 5b `download_image` function).
3. Re-render only the affected card slice (pass the single HTML file to `slice.js --input`).
4. Re-check manifest before continuing.

**Token validation (text components):**
- [ ] No `{{` or `}}` characters remain in any text component HTML
- [ ] `{{ unsubscribe_url }}` is present in footer with single braces and internal spaces

**Content checks:**
- [ ] Cervanttis headlines (hero, upsell-noir, opt-out) are lowercase in token values
- [ ] Lust headlines (body-copy, section-headline, product cards) are sentence case
- [ ] `REVIEW_STARS` uses `★` Unicode characters

---

## Step 7: Preview

Assemble a preview email that mixes local slice paths (for review) with the text HTML blocks.

**Preview assembly structure** (table-based, 600px wide):
```
[header slice img — local path]
[hero slice img — local path]
[opt-out HTML — if required]
[body-copy slice img — local path]
[section-headline HTML]
[product card slices — local paths, wrapped in <a href>]
[testimonial slice — local path]
[upsell slice — local path, wrapped in <a href>]
[delivery-cutoffs HTML — if required]
[trust-bar slice — local path]
[footer HTML]
```

For preview, slice `<img>` tags use `file://` local paths. These will be replaced with Klaviyo CDN URLs in Step 9.

Save preview HTML to Google Drive only — do not write preview HTML to local disk. Read `reference-google-drive` skill for conventions:
- Folder: use the Step 7a run folder (`Campaign Drafts/{YYYYMMDDhhmm}/{campaign-slug}-{run-id}`)
- Title: `{YYYY-MM-DD} {Campaign Name} — Design Preview`
- mimeType: `text/html`, disableConversionToGoogleType: `true`
- Use `GWS_USER_ADMIN` credentials for all Drive API calls (see **Google Workspace Credentials** section above)

State: *"Preview uses locally-rendered PNG slices — fonts, illustrations, and layout are browser-rendered and pixel-accurate. Review at 600px width."*

### Step 7a: Create deterministic run-scoped Drive folders

Before uploading any preview/production artifacts, create and use nested subfolders under the Campaign Drafts parent. Use `GWS_USER_ADMIN` for all Drive folder creation calls:

```bash
env -u GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE \
  GOOGLE_WORKSPACE_CLI_CONFIG_DIR=$GWS_USER_ADMIN \
  gws drive files create \
  --json '{"name": "{TIMESTAMP_YYYYMMDDHHMM}", "mimeType": "application/vnd.google-apps.folder", "parents": ["14SJXWGGrZAoJUmkEb0FlBDSHHNyf_bIj"]}' \
  --params '{"fields": "id,name,webViewLink", "supportsAllDrives": true}'
```

1. Compute `TIMESTAMP_YYYYMMDDHHMM` in UTC by default (`YYYYMMDDhhmm`, 24-hour clock).
2. If the caller explicitly provides a timezone override, compute the same format in that timezone.
3. Under parent `Campaign Drafts` (`14SJXWGGrZAoJUmkEb0FlBDSHHNyf_bIj`), create/use:
   - timestamp folder: `{TIMESTAMP_YYYYMMDDHHMM}`
   - run folder inside timestamp folder: `{campaign-slug}-{run-id}`
4. Save all campaign artifacts (preview HTML, production HTML, and any optional packaging files) into this run folder.
5. In run comments, always include links to:
   - Campaign Drafts parent folder
   - timestamp folder
   - run folder
   - uploaded artifact files

This structure is required to avoid destination collisions across concurrent runs and to keep outputs traceable.

**Wait for explicit human approval before proceeding to Step 8.**

If edits are requested:
- **Copy changes** → update token values, re-render affected slices, re-assemble
- **Component changes** → update selection, re-render, re-assemble
- **Visual/design changes** → these require a template file update. Flag to human.

---

## Step 8: Upload slices to Klaviyo

Upload each PNG slice from `/tmp/[campaign-slug]/slices/` to the Klaviyo media library.

```
POST /api/images/
```

Note the returned Klaviyo CDN URL for each slice. Store as a mapping:
```json
{
  "header": "https://cdn.klaviyo.com/media/.../header.png",
  "hero-a": "https://cdn.klaviyo.com/media/.../hero-a.png",
  "product-card-1": "https://cdn.klaviyo.com/media/.../product-card-1.png",
  ...
}
```

See `references/klaviyo-html.md` for the image upload API spec.

## Step 9: Production HTML

Assemble the final email HTML using Klaviyo CDN slice URLs (replacing local file paths).

**Production assembly rules:**
- All slice `<img>` tags: `src` = Klaviyo CDN URL, `width="600"`, `style="display:block;width:600px;"`
- All CTAs: slice `<img>` wrapped in `<a href="{{CTA_URL}}">`
- Decorative slices: empty `alt=""`
- Hero/product slices: descriptive `alt="{{HEADLINE}}"` or `alt="{{PRODUCT_NAME}}"`
- Text components: inserted as raw HTML (no shell wrapper needed — inline styles only)
- Unsubscribe: `{{ unsubscribe_url }}` in footer — exact Klaviyo syntax

Save to Google Drive only — do not write production HTML to local disk:
- Folder: use the Step 7a run folder (`Campaign Drafts/{YYYYMMDDhhmm}/{campaign-slug}-{run-id}`)
- Title: `{YYYY-MM-DD} {Campaign Name} — Production HTML`
- mimeType: `text/html`, disableConversionToGoogleType: `true`
- Use `GWS_USER_ADMIN` credentials for all Drive API calls (see **Google Workspace Credentials** section above)

**Font check:** grep production HTML for `base64` in `<style>` blocks. Should find none — the production email has no embedded fonts, only Klaviyo-hosted slice images.

**Wait for explicit human approval before proceeding to Step 10.**

---

## Step 10: Klaviyo Deployment

Read `references/klaviyo-html.md` before making API calls.

**Create template:**
```
POST /api/templates/
{
  "data": {
    "type": "template",
    "attributes": {
      "name": "{Campaign Name} — {YYYY-MM-DD}",
      "editor_type": "CODE",
      "html": "{production_html}"
    }
  }
}
```

Assign template to campaign message. Set list/segment and scheduled send time.

Wait 2–3 seconds after template creation before any follow-up API call (known Klaviyo 404 bug).

**Confirm with human before scheduling send. Never auto-send.**

---

## Template library reference

All templates are in `references/templates/`. Always read the actual file — never reconstruct template HTML from memory.

Read `references/manifest.json` to confirm exact file paths and token names before assembly.

| Reference file | Read before... |
|---|---|
| `references/brand-voice.md` | Writing any copy (Step 3) |
| `references/product-selection.md` | Selecting products (Step 2) |
| `references/manifest.json` | Component selection and token names (Steps 4–5) |
| `references/klaviyo-html.md` | Klaviyo API calls (Steps 8, 10) |
| `reference-google-drive` skill | Google Drive uploads (Steps 7, 9) — use `$GWS_USER_ADMIN` |
| `puppeteer` skill | Slice rendering (Step 5) — must be installed on VPS first |

---

## Product-card / product-grid regression checklist

Run this checklist any time a campaign includes product card slices before proceeding to Step 7:

- [ ] **URL preflight passed** — every product image URL returned `Content-Type: image/*` before download
- [ ] **All images downloaded** — every `file://` path referenced in component HTML exists on disk
- [ ] **MIME check passed** — every downloaded file identified as `image/*` by `file --mime-type`
- [ ] **Byte-size check passed** — no downloaded file is under 5KB
- [ ] **Per-card broken_images empty** — `broken_images: []` for every card entry in `__SLICE_MANIFEST__`
- [ ] **Grid aggregate check passed** — zero broken-image indicators across all `card-*` and `product-*` slices combined
- [ ] **Visual spot-check** — open at least one product card PNG and confirm the product photo renders (not a grey placeholder or browser broken-image icon)

---

## Troubleshooting

### `minimist` not found when running slice.js

**Symptom:**
```
Error: Cannot find module 'minimist'
    at Function.Module._resolveFilename (node:internal/modules/cjs/loader:1039:15)
```

**Cause:** The `reference-puppeteer` skill's npm dependencies have not been installed, or were installed in the wrong directory.

**Fix:**
```bash
# Navigate to the puppeteer skill's references directory and install deps
cd [puppeteer-skill-path]/references
npm install

# Verify
node -e "require('minimist'); console.log('minimist OK')"
node -e "require('puppeteer'); console.log('puppeteer OK')"
```

The `references/` directory contains `package.json` with `minimist` and `puppeteer` as dependencies. Running `npm install` inside that directory is the only setup step needed. Do not run `npm install` at the repo root.

### Product images render as broken placeholders despite successful slice.js run

**Symptom:** slice.js exits 0 and produces PNGs, but the PNG shows a grey box or browser broken-image icon where the product photo should be.

**Cause:** `file://` path in the component HTML is wrong — mismatched slug, extension, or directory path.

**Fix:**
1. Open the failing component HTML file and find the `<img src="file:///...">` value.
2. Check that exact path exists: `ls -lh "file-path-here"` (strip `file://` prefix).
3. If missing, re-run the `download_image` function from Step 5b for that URL.
4. If the path is wrong, correct the token value in the component HTML and re-render.

### `broken_images` non-empty for a slice but PNG looks correct

**Symptom:** `__SLICE_MANIFEST__` reports `broken_images` for a slice, but the PNG appears correct when opened.

**Cause:** Puppeteer flagged an image that loaded with zero natural dimensions (e.g., a 1×1 tracking pixel, SVG with no intrinsic size). This is usually harmless for illustration assets but should be investigated.

**Fix:** Check each URL in `broken_images`:
- If it's a decoration/illustration asset, confirm it renders visually in the PNG — if so, it can be treated as a known false positive.
- If it's a product image, treat as broken and re-download.
- Never mark a broken product image as an acceptable false positive.

---

## What the agent does NOT do in v4

- Write HTML
- Choose colours, fonts, or spacing
- Resize or reposition illustrations
- Add, remove, or modify SVG icons
- Override any locked style in a template

If a campaign need cannot be met with the existing templates, escalate for template development. Do not improvise HTML.
