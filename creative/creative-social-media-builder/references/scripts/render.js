#!/usr/bin/env node
/**
 * render.js — Fill tokens into a locked social-media template and render a flat
 * PNG creative via headless Chromium. The social-media equivalent of the email
 * builder's slice.js: token-inject → headless render → validate. Reuses the
 * `puppeteer` skill's installed Chromium (require resolves from the skill's
 * node_modules; see SKILL.md "Dependency").
 *
 * Usage:
 *   node render.js --template t1-quote --tokens vals.json --ratio 1080x1920 --output out.png
 *   node render.js --template t1-quote --tokens vals.json --all-ratios --output-dir ./out
 *
 * Options:
 *   --template   <id|path>   Template id from manifest.json (e.g. "t1-quote") OR a path to an .html template.
 *   --tokens     <path>      JSON file of { TOKEN: "value" } pairs. Optional if the template has no tokens.
 *   --ratio      <WxH>       "1080x1920" (story) or "1080x1350" (post). Default 1080x1920.
 *   --all-ratios             Render BOTH ratios. Requires --output-dir.
 *   --output     <path>      Output PNG path (single ratio).
 *   --output-dir <path>      Output directory (used with --all-ratios; files named <template>-<ratio>.png).
 *   --shell      <name>      "preview" (base64 fonts, default) or "production" (CDN fonts).
 *   --scale      <n>         Device scale factor. Default 1 (1080px wide IS the target; use 2 only for proofing).
 *   --skill-dir  <path>      Skill root. Default: two levels up from this script.
 *   --puppeteer  <path>      Path to a node_modules dir that has puppeteer. Default: the reference-puppeteer skill.
 *   --verbose                Log progress.
 *
 * Emits a __RENDER_MANIFEST__ … __END_MANIFEST__ JSON block on stdout (parsed in SKILL Step 6).
 * Exit code is non-zero on any hard failure (unfilled token, wrong dimensions, content overflow).
 */
'use strict';

const fs = require('fs');
const path = require('path');

// Dependencies (minimist, puppeteer) live in the reference-puppeteer skill's
// node_modules — installed once via `npm install` there. Make them resolvable
// regardless of where this script is invoked from.
(function addDepPaths() {
  const here = __dirname;
  const candidates = [
    process.env.PUPPETEER_SKILL_NODE_MODULES,
    path.join(here, '..', '..', '..', '..', 'reference', 'reference-puppeteer', 'references', 'node_modules'),
    path.join(here, '..', 'node_modules'),
  ].filter(Boolean);
  for (const c of candidates) { if (fs.existsSync(c) && !module.paths.includes(c)) module.paths.unshift(c); }
})();

const args = require('minimist')(process.argv.slice(2), { boolean: ['all-ratios', 'verbose'] });

const SKILL_DIR = path.resolve(args['skill-dir'] || path.join(__dirname, '..', '..'));
const REF = path.join(SKILL_DIR, 'references');
const RATIOS = { '1080x1920': { w: 1080, h: 1920, kind: 'story' }, '1080x1350': { w: 1080, h: 1350, kind: 'post' } };
const SCALE = parseInt(args.scale || 1, 10);
const SHELL = (args.shell || 'preview') === 'production' ? 'shell-production.html' : 'shell-preview.html';

// Backward-compatible defaults for optional LAYOUT tokens (T4 placement etc.).
// Templates that don't reference them ignore them; templates that do get a sane
// value when the caller omits them. Caller tokens always win.
const LAYOUT_DEFAULTS = { PHOTO_POS: 'center', BAR_ANCHOR: 'bottom:140px', CTA_SIZE: '20px' };

// Contrast thresholds (WCAG-style). Text over a photo is checked against the
// band luminance sampled from the rendered PNG. See analyseContrast().
const CONTRAST_FAIL = 3.0;   // below this → hard error (illegible)
const CONTRAST_WARN = 4.5;   // below this → warning (AA large-text floor)
const BAND_STDEV_WARN = 0.16; // luminance stdev (0..1) above this → textured/shadowed band

function info(...m) { if (args.verbose) console.log('[render]', ...m); }
function fail(...m) { console.error('[render] ERROR:', ...m); process.exit(1); }

// --- Contrast helpers ----------------------------------------------------
// Parse "#rgb" / "#rrggbb" / "rgb()" / "rgba()" → [r,g,b] 0..255 (alpha ignored).
function parseColor(c) {
  if (!c) return null;
  c = String(c).trim();
  let m = c.match(/^#([0-9a-f]{3})$/i);
  if (m) return m[1].split('').map(h => parseInt(h + h, 16));
  m = c.match(/^#([0-9a-f]{6})$/i);
  if (m) return [0, 2, 4].map(i => parseInt(m[1].substr(i, 2), 16));
  m = c.match(/rgba?\(([^)]+)\)/i);
  if (m) { const p = m[1].split(',').map(s => parseFloat(s)); return [p[0], p[1], p[2]]; }
  return null;
}
function relLuminance([r, g, b]) {
  const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}
function contrastRatio(l1, l2) { const a = Math.max(l1, l2), b = Math.min(l1, l2); return (a + 0.05) / (b + 0.05); }

// Mean + stdev of per-pixel relative luminance in the HALO around the caption
// glyphs: pixels inside `outerPx` but outside the tight text box `innerPx`. The
// halo is what governs legibility — for a white box it reads white, for a solid
// bg it reads the bg, for a photo it reads the local band (and a shadow/edge
// crossing the text shows up as high stdev).
function sampleBandLuminance(png, outerPx, innerPx) {
  const { width, data } = png;
  const x0 = Math.max(0, Math.floor(outerPx.left)), x1 = Math.min(width, Math.ceil(outerPx.right));
  const y0 = Math.max(0, Math.floor(outerPx.top)), y1 = Math.min(png.height, Math.ceil(outerPx.bottom));
  const iL = Math.floor(innerPx.left), iR = Math.ceil(innerPx.right);
  const iT = Math.floor(innerPx.top), iB = Math.ceil(innerPx.bottom);
  const lums = [];
  for (let y = y0; y < y1; y += 2) {
    for (let x = x0; x < x1; x += 2) {
      if (x >= iL && x < iR && y >= iT && y < iB) continue; // skip the glyph box
      const i = (y * width + x) * 4;
      lums.push(relLuminance([data[i], data[i + 1], data[i + 2]]));
    }
  }
  if (!lums.length) return null;
  const mean = lums.reduce((a, b) => a + b, 0) / lums.length;
  const variance = lums.reduce((a, b) => a + (b - mean) * (b - mean), 0) / lums.length;
  return { mean, stdev: Math.sqrt(variance), n: lums.length };
}

// Resolve puppeteer from the reference-puppeteer skill (installed once via npm install there).
function loadPuppeteer() {
  const candidates = [];
  if (args.puppeteer) candidates.push(path.resolve(args.puppeteer, 'puppeteer'));
  candidates.push('puppeteer'); // if hoisted / globally resolvable
  candidates.push(path.join(SKILL_DIR, '..', '..', 'reference', 'reference-puppeteer', 'references', 'node_modules', 'puppeteer'));
  for (const c of candidates) {
    try { return require(c); } catch (_) { /* try next */ }
  }
  fail('Could not require puppeteer. Run `npm install` in reference-puppeteer/references, or pass --puppeteer <node_modules path>.');
}

function resolveTemplate(t) {
  if (t.endsWith('.html')) return path.resolve(t);
  const manifestPath = path.join(REF, 'manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const entry = manifest.templates.find(x => x.id.toLowerCase() === t.toLowerCase() || path.basename(x.file, '.html') === t);
  if (!entry) fail(`Template "${t}" not found in manifest.json. Known ids: ${manifest.templates.map(x => x.id).join(', ')}`);
  return path.join(REF, entry.file);
}

function fillTokens(html, tokens, ratioKey) {
  const r = RATIOS[ratioKey];
  const assetsBase = 'file://' + path.join(REF, 'illustrations');
  let out = html
    .split('{{ASSETS_BASE}}').join(assetsBase)
    .split('{{CANVAS_W}}').join(String(r.w))
    .split('{{CANVAS_H}}').join(String(r.h))
    .split('{{RATIO}}').join(ratioKey)
    .split('{{RATIO_KIND}}').join(r.kind);
  for (const [k, v] of Object.entries(tokens)) {
    out = out.split('{{' + k + '}}').join(v == null ? '' : String(v));
  }
  return out;
}

// Any {{TOKEN}} left after filling is a hard error, EXCEPT shell content marker.
function unfilledTokens(html) {
  const found = new Set();
  const re = /\{\{([A-Z0-9_]+)\}\}/g;
  let m;
  while ((m = re.exec(html))) { if (m[1] !== 'CONTENT') found.add(m[1]); }
  return [...found];
}

async function renderOne(puppeteer, templateFile, tokens, ratioKey, outPath) {
  const r = RATIOS[ratioKey];
  if (!r) fail(`Unknown ratio "${ratioKey}". Use 1080x1920 or 1080x1350.`);

  const templateHtml = fs.readFileSync(templateFile, 'utf8');
  const shellHtml = fs.readFileSync(path.join(REF, 'shell', SHELL), 'utf8');

  // Fill the template first, then drop it into the shell, then fill shell-level tokens.
  const content = fillTokens(templateHtml, tokens, ratioKey);
  let page = shellHtml
    .split('{{CONTENT}}').join(content)
    .split('{{CANVAS_W}}').join(String(r.w))
    .split('{{CANVAS_H}}').join(String(r.h))
    .split('{{RATIO}}').join(ratioKey)
    .split('{{TITLE}}').join(tokens.TITLE || `Fig & Bloom — ${path.basename(templateFile, '.html')}`);

  const leftover = unfilledTokens(page);
  if (leftover.length) fail(`Unfilled tokens for ${path.basename(templateFile)} @ ${ratioKey}: ${leftover.join(', ')}`);

  const tmpHtml = outPath.replace(/\.png$/i, '') + `.${ratioKey}.html`;
  fs.mkdirSync(path.dirname(path.resolve(outPath)), { recursive: true });
  fs.writeFileSync(tmpHtml, page);
  info(`wrote ${tmpHtml}`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--font-render-hinting=none'],
  });
  const pg = await browser.newPage();
  await pg.setViewport({ width: r.w, height: r.h, deviceScaleFactor: SCALE });
  await pg.goto('file://' + path.resolve(tmpHtml), { waitUntil: 'networkidle0', timeout: 30000 });
  await pg.evaluate(() => document.fonts.ready);

  // Diagnostics from inside the page: canvas size, content overflow, broken images.
  const diag = await pg.evaluate(() => {
    const c = document.getElementById('canvas');
    const cb = c.getBoundingClientRect();
    const broken = [];
    document.querySelectorAll('img').forEach(img => {
      if (!img.complete || img.naturalWidth === 0) broken.push(img.getAttribute('src') || '(no src)');
    });
    // Largest overflow of any descendant beyond the canvas box.
    let overRight = 0, overBottom = 0;
    c.querySelectorAll('*').forEach(el => {
      const b = el.getBoundingClientRect();
      overRight = Math.max(overRight, Math.round(b.right - cb.right));
      overBottom = Math.max(overBottom, Math.round(b.bottom - cb.bottom));
    });

    // Collect on-image text candidates for the contrast validator. For each, get
    // the TIGHT text box (via a Range) and a local "band" strip beside the text.
    const captions = [];
    const SEL = '.caption, .phrase, .quote, .headline, .line, .label, .attr-name, .overline';
    c.querySelectorAll(SEL).forEach(el => {
      const txt = (el.textContent || '').trim();
      if (!txt) return;
      let tr;
      try { const rg = document.createRange(); rg.selectNodeContents(el); tr = rg.getBoundingClientRect(); }
      catch (_) { tr = el.getBoundingClientRect(); }
      if (!tr || tr.width < 4 || tr.height < 4) return;
      const color = getComputedStyle(el).color;
      const pad = Math.max(10, 0.35 * tr.height); // halo thickness around the glyphs
      const inner = { left: tr.left - cb.left, right: tr.right - cb.left, top: tr.top - cb.top, bottom: tr.bottom - cb.top };
      const outer = {
        left: Math.max(cb.left, tr.left - pad) - cb.left,
        right: Math.min(cb.right, tr.right + pad) - cb.left,
        top: Math.max(cb.top, tr.top - pad) - cb.top,
        bottom: Math.min(cb.bottom, tr.bottom + pad) - cb.top,
      };
      captions.push({ cls: el.className, color, outer, inner });
    });

    return {
      canvasW: Math.round(cb.width), canvasH: Math.round(cb.height),
      scrollW: c.scrollWidth, scrollH: c.scrollHeight,
      clientW: c.clientWidth, clientH: c.clientHeight,
      overRight, overBottom, broken, captions,
    };
  });

  const el = await pg.$('#canvas');
  await el.screenshot({ path: outPath, type: 'png' });
  await browser.close();

  const stat = fs.statSync(outPath);
  const expectW = r.w * SCALE, expectH = r.h * SCALE;

  const TOL = 2; // px tolerance for sub-pixel rounding
  const result = {
    template: path.basename(templateFile),
    ratio: ratioKey,
    output: path.resolve(outPath),
    bytes: stat.size,
    expected: { w: expectW, h: expectH },
    canvas: { w: diag.canvasW, h: diag.canvasH },
    overflow: { right: Math.max(0, diag.overRight), bottom: Math.max(0, diag.overBottom),
                scroll: Math.max(0, diag.scrollH - diag.clientH) },
    broken_images: diag.broken,
    contrast: [],
    errors: [],
    warnings: [],
  };
  if (Math.abs(diag.canvasW - r.w) > TOL || Math.abs(diag.canvasH - r.h) > TOL)
    result.errors.push(`canvas ${diag.canvasW}x${diag.canvasH} != target ${r.w}x${r.h}`);
  if (result.overflow.right > TOL || result.overflow.bottom > TOL || result.overflow.scroll > TOL)
    result.errors.push(`content overflow (right:${result.overflow.right} bottom:${result.overflow.bottom} scroll:${result.overflow.scroll}) — text/photo exceeds the ${ratioKey} canvas; shorten copy or pick the other ratio`);
  if (diag.broken.length) result.errors.push(`broken images: ${diag.broken.join(', ')}`);

  // --- Contrast validator: sample the band behind each on-image text element
  // from the rendered PNG and check legibility against the text colour. Solid
  // backgrounds read as uniform high-contrast and pass; photo bands get a real
  // check. Catches T4/T3-style legibility failures (and shadowed/textured bands)
  // automatically, so the agent self-corrects instead of relying on eyeballing.
  try {
    const PNG = require('pngjs').PNG;
    const png = PNG.sync.read(fs.readFileSync(outPath));
    for (const cap of (diag.captions || [])) {
      const ink = parseColor(cap.color);
      if (!ink) continue;
      const toPx = o => ({ left: o.left * SCALE, right: o.right * SCALE, top: o.top * SCALE, bottom: o.bottom * SCALE });
      const band = sampleBandLuminance(png, toPx(cap.outer), toPx(cap.inner));
      if (!band) continue;
      const inkL = relLuminance(ink);
      const ratio = contrastRatio(inkL, band.mean);
      const entry = {
        el: cap.cls, contrast: Math.round(ratio * 100) / 100,
        band_stdev: Math.round(band.stdev * 1000) / 1000,
      };
      result.contrast.push(entry);
      const where = `${cap.cls} (contrast ${entry.contrast}:1`;
      if (ratio < CONTRAST_FAIL)
        result.errors.push(`${where}, < ${CONTRAST_FAIL}:1) — caption illegible on this band; switch ink (white over dark, dark over light) or move the caption to a cleaner band`);
      else if (ratio < CONTRAST_WARN)
        result.warnings.push(`${where}, < ${CONTRAST_WARN}:1) — low contrast; consider a cleaner band, opposite ink, or the serif-box fallback`);
      if (band.stdev > BAND_STDEV_WARN)
        result.warnings.push(`${cap.cls} sits on a textured/shadowed band (luminance stdev ${entry.band_stdev}) — legibility is unreliable even if mean contrast passes; pick a uniform band or use the serif-box fallback`);
    }
  } catch (e) {
    result.warnings.push(`contrast check skipped: ${e.message}`);
  }

  info(`✓ ${outPath} (${Math.round(stat.size / 1024)}KB) ${result.errors.length ? 'WITH ERRORS' : 'clean'}`);
  return result;
}

async function main() {
  if (!args.template) fail('--template is required');
  const templateFile = resolveTemplate(args.template);
  const tokens = Object.assign({}, LAYOUT_DEFAULTS, args.tokens ? JSON.parse(fs.readFileSync(path.resolve(args.tokens), 'utf8')) : {});
  const puppeteer = loadPuppeteer();

  const jobs = [];
  if (args['all-ratios']) {
    const dir = args['output-dir'] || '.';
    const base = path.basename(templateFile, '.html');
    for (const rk of Object.keys(RATIOS)) jobs.push([rk, path.join(dir, `${base}-${rk}.png`)]);
  } else {
    const rk = args.ratio || '1080x1920';
    if (!args.output) fail('--output is required (or use --all-ratios with --output-dir)');
    jobs.push([rk, args.output]);
  }

  const results = [];
  for (const [rk, out] of jobs) results.push(await renderOne(puppeteer, templateFile, tokens, rk, out));

  const anyErr = results.some(r => r.errors.length);
  console.log('__RENDER_MANIFEST__');
  console.log(JSON.stringify({ ok: !anyErr, results }, null, 2));
  console.log('__END_MANIFEST__');
  process.exit(anyErr ? 1 : 0);
}

main().catch(e => fail(`Fatal: ${e.message}`));
