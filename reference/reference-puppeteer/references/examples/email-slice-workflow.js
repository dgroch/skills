/**
 * example: email-slice-workflow.js
 *
 * Demonstrates how the email-campaign-builder skill calls slice.js
 * to render visual components into PNG slices.
 *
 * This is REFERENCE CODE for the agent — not a script to run directly.
 * The agent executes these steps via bash tool calls.
 */

// ── Step 1: Agent has assembled token-filled component HTML files ─────────────
//
// After filling tokens, the agent saves each visual component as a
// standalone HTML file in a working directory. Each file is a complete
// HTML document using shell-preview.html (base64 fonts for correct render).
//
// Working directory structure:
//   /tmp/campaign-mothers-day-2026/components/
//     hero-a.html
//     product-card-1.html       (card-horizontal, filled tokens)
//     product-card-2.html       (card-horizontal-reversed, filled tokens)
//     testimonial.html
//     upsell-noir.html
//     trust-bar.html

// ── Step 2: Agent calls slice.js ──────────────────────────────────────────────
//
// bash tool call:
//   node /path/to/puppeteer/references/scripts/slice.js \
//     --input /tmp/campaign-mothers-day-2026/components/ \
//     --output /tmp/campaign-mothers-day-2026/slices/ \
//     --width 600 \
//     --scale 2 \
//     --verbose
//
// Output: one PNG per component, 1200px wide (retina), auto-height cropped
//   /tmp/campaign-mothers-day-2026/slices/
//     hero-a.png
//     product-card-1.png
//     product-card-2.png
//     testimonial.png
//     upsell-noir.png
//     trust-bar.png

// ── Step 3: Agent uploads slices to Klaviyo media library ────────────────────
//
// POST /api/images/ for each PNG
// Note the returned hosted URL for each slice.
//
// Example URLs:
//   https://cdn.klaviyo.com/media/[account]/hero-a.png
//   https://cdn.klaviyo.com/media/[account]/product-card-1.png

// ── Step 4: Agent assembles final email HTML ──────────────────────────────────
//
// The final email mixes <img> slices with plain HTML text blocks.
// Only these components remain as HTML (single-column text — safe in all clients):
//   - opt-out section
//   - body-copy section
//   - section-headline
//   - delivery-cutoffs
//   - footer (with {{ unsubscribe_url }})
//   - divider-line (1px rule)
//   - divider-whitespace (48px gap)
//
// Example final assembly:
const FINAL_EMAIL_STRUCTURE = `
<!-- HEADER SLICE -->
<tr><td style="padding:0;">
  <img src="https://cdn.klaviyo.com/media/[account]/header.png"
       width="600" alt="" style="display:block;width:600px;">
</td></tr>

<!-- HERO SLICE -->
<tr><td style="padding:0;">
  <a href="{{CTA_URL}}">
    <img src="https://cdn.klaviyo.com/media/[account]/hero-a.png"
         width="600" alt="{{HERO_ALT_TEXT}}" style="display:block;width:600px;">
  </a>
</td></tr>

<!-- OPT-OUT: HTML text block -->
{{opt-out template HTML}}

<!-- BODY COPY: HTML text block -->
{{body-copy template HTML}}

<!-- PRODUCT CARD 1 SLICE -->
<tr><td style="padding:0;">
  <a href="{{PRODUCT_1_URL}}">
    <img src="https://cdn.klaviyo.com/media/[account]/product-card-1.png"
         width="600" alt="{{PRODUCT_1_NAME}}" style="display:block;width:600px;">
  </a>
</td></tr>

<!-- PRODUCT CARD 2 SLICE -->
<tr><td style="padding:0;">
  <a href="{{PRODUCT_2_URL}}">
    <img src="https://cdn.klaviyo.com/media/[account]/product-card-2.png"
         width="600" alt="{{PRODUCT_2_NAME}}" style="display:block;width:600px;">
  </a>
</td></tr>

<!-- TESTIMONIAL SLICE -->
<tr><td style="padding:0;">
  <img src="https://cdn.klaviyo.com/media/[account]/testimonial.png"
       width="600" alt="" style="display:block;width:600px;">
</td></tr>

<!-- UPSELL SLICE -->
<tr><td style="padding:0;">
  <a href="{{UPSELL_URL}}">
    <img src="https://cdn.klaviyo.com/media/[account]/upsell-noir.png"
         width="600" alt="{{UPSELL_CTA_TEXT}}" style="display:block;width:600px;">
  </a>
</td></tr>

<!-- DELIVERY CUTOFFS: HTML text block -->
{{delivery-cutoffs template HTML}}

<!-- TRUST BAR SLICE -->
<tr><td style="padding:0;">
  <img src="https://cdn.klaviyo.com/media/[account]/trust-bar.png"
       width="600" alt="" style="display:block;width:600px;">
</td></tr>

<!-- FOOTER: HTML text block -->
{{footer template HTML}}
`;

// ── Key rules for agents ──────────────────────────────────────────────────────
//
// 1. ALWAYS wrap slice <img> tags in <a href> when the component has a CTA.
//    Images are not clickable by default — the link must be explicit.
//
// 2. ALWAYS include alt text on slice images:
//    - Hero/product slices: descriptive alt (product name, headline)
//    - Decorative slices (testimonial, trust-bar): empty alt=""
//
// 3. ALWAYS set width="600" and style="display:block;width:600px;" on every
//    slice <img> — prevents email clients from resizing images unexpectedly.
//
// 4. divider-line and divider-whitespace are NOT sliced — use HTML.
//    A 1px line and a 48px spacer are simpler and more reliable as HTML.
//
// 5. Illustration strip dividers (divider-illo-*) ARE sliced — they contain
//    complex CSS background-image positioning that doesn't render in all clients.
