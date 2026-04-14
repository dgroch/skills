---
name: reference-puppeteer
description: Headless browser utilities — screenshot, slice HTML components to PNG, render PDFs. Use this skill whenever an agent needs to: capture a screenshot of a URL, render an HTML file to PNG, slice HTML email components into image files, or generate a PDF from an HTML document.
---

# Puppeteer Skill

Provides headless Chromium rendering for Paperclip agents via three scripts:

| Script                          | Purpose                                                        |
| ------------------------------- | -------------------------------------------------------------- |
| `references/scripts/slice.js`   | Render HTML files → PNG slices (primary use: email components) |
| `references/scripts/capture.js` | Screenshot a live URL or local HTML file                       |
| `references/scripts/pdf.js`     | Render HTML → PDF                                              |

---

## Prerequisites

One-time setup required on the VPS. Read `references/INSTALL.md` and follow all steps before first use. Key requirements:

- Node.js ≥ 18
- System libraries installed via apt-get
- `npm install` run inside `references/` to download Puppeteer + Chromium

Verify with: `node -e "require('puppeteer'); console.log('OK')"`

---

## Script 1: slice.js

Renders one or more HTML component files to PNG images. Each HTML file becomes one PNG, auto-cropped to exact content height. Designed for email component slicing.

```bash
# Single file
node references/scripts/slice.js \
  --input ./components/hero-a.html \
  --output ./slices/ \
  --assets /path/to/email-campaign-builder/references/assets

# Directory of files (processes all .html files)
node references/scripts/slice.js \
  --input ./components/ \
  --output ./slices/ \
  --assets /path/to/email-campaign-builder/references/assets \
  --width 600 \
  --scale 2 \
  --verbose
```

**Options:**

| Flag        | Default  | Description                                            |
| ----------- | -------- | ------------------------------------------------------ |
| `--input`   | required | HTML file or directory                                 |
| `--output`  | required | Output directory                                       |
| `--assets`  | required | Absolute path to assets folder (illustrations)         |
| `--width`   | `600`    | CSS pixel width (use 600 for email)                    |
| `--scale`   | `2`      | Device scale factor (2 = retina, 1200px actual output) |
| `--timeout` | `10000`  | Max render time per file in ms                         |
| `--verbose` | off      | Detailed logging                                       |

**Output:** PNG files named after input HTML files. At default settings, each PNG is 1200px wide (600px × 2x scale) — retina-ready for email.

**The script outputs a JSON manifest** between `__SLICE_MANIFEST__` markers on stdout. Parse this to get the exact output paths:

```json
{
  "slices": [
    {
      "file": "hero-a.png",
      "path": "/absolute/path/to/slices/hero-a.png",
      "width_css_px": 600,
      "scale": 2,
      "width_actual_px": 1200
    }
  ]
}
```

---

## Script 2: capture.js

Screenshots a live URL or local HTML file.

```bash
# Full-page screenshot of a URL
node references/scripts/capture.js \
  --url https://figandbloom.com \
  --output ./screenshot.png \
  --full-page

# Specific element only
node references/scripts/capture.js \
  --url https://figandbloom.com \
  --output ./hero.png \
  --selector ".hero-section"

# Local HTML file
node references/scripts/capture.js \
  --file ./preview.html \
  --output ./preview.png \
  --width 600
```

**Options:**

| Flag          | Default  | Description                                          |
| ------------- | -------- | ---------------------------------------------------- |
| `--url`       | —        | Live URL to capture (mutually exclusive with --file) |
| `--file`      | —        | Local HTML file to capture                           |
| `--output`    | required | Output PNG path                                      |
| `--width`     | `1440`   | Viewport width                                       |
| `--height`    | `900`    | Viewport height                                      |
| `--scale`     | `1`      | Device scale factor                                  |
| `--full-page` | off      | Capture full scrollable page                         |
| `--selector`  | —        | CSS selector — capture one element only              |
| `--wait`      | `0`      | Extra wait after load (ms) — useful for animations   |
| `--timeout`   | `15000`  | Navigation timeout (ms)                              |

---

## Script 3: pdf.js

Renders an HTML file to PDF.

```bash
node references/scripts/pdf.js \
  --input ./report.html \
  --output ./report.pdf \
  --format A4 \
  --margin 48
```

**Options:**

| Flag              | Default  | Description                      |
| ----------------- | -------- | -------------------------------- |
| `--input`         | required | HTML file to render              |
| `--output`        | required | Output PDF path                  |
| `--format`        | `A4`     | Page size (A4, Letter, A3, etc.) |
| `--margin`        | `40`     | Uniform page margin in px        |
| `--landscape`     | off      | Landscape orientation            |
| `--no-background` | off      | Omit background colours/images   |
| `--timeout`       | `15000`  | Navigation timeout (ms)          |

---

## Email component slicing workflow

This is the primary use case. Read `references/examples/email-slice-workflow.js` for the full annotated workflow. Summary:

### Which components to slice vs keep as HTML

**Slice to PNG** (visual components with layout, illustrations, fonts):

- header
- all hero variants (hero-a, hero-b-*, hero-c*, hero-d-*)
- all product cards
- testimonial
- upsell-noir
- trust-bar
- divider-illo-* (illustration strip dividers)

**Keep as HTML** (single-column text — safe in all clients):

- opt-out
- body-copy
- section-headline
- delivery-cutoffs
- footer
- divider-line (1px rule)
- divider-whitespace (48px gap)

### Linking slices

Every slice with a CTA must be wrapped in `<a href>` — the image itself is not clickable:

```html
<tr><td style="padding:0;">
  <a href="{{CTA_URL}}">
    <img src="{{SLICE_KLAVIYO_URL}}"
         width="600"
         alt="{{DESCRIPTIVE_ALT_TEXT}}"
         style="display:block;width:600px;">
  </a>
</td></tr>
```

Decorative slices (no CTA) use empty alt and no link:

```html
<tr><td style="padding:0;">
  <img src="{{SLICE_KLAVIYO_URL}}"
       width="600"
       alt=""
       style="display:block;width:600px;">
</td></tr>
```

### Slice upload

After slicing, upload each PNG to the Klaviyo media library:

```
POST /api/images/
Content-Type: multipart/form-data
```

See the klaviyo-api skill or `references/klaviyo-html.md` in the email skill for the full upload spec.

---

## Other use cases

- **QA screenshots** — capture campaign preview pages before sending
- **Competitor research** — screenshot competitor sites at a point in time
- **PDF reports** — render data/analytics HTML reports to PDF for sharing
- **OG image capture** — screenshot pages to verify social share images
- **Visual regression** — capture before/after screenshots when deploying Shopify theme changes

---

## Error handling

All scripts exit with code `1` on failure and print an error to stderr. The agent should check the exit code:

```bash
node references/scripts/slice.js --input ./components/ --output ./slices/
if [ $? -ne 0 ]; then
  echo "Slice rendering failed"
  exit 1
fi
```

Common errors and fixes are documented in `references/INSTALL.md`.
