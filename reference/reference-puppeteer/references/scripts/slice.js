#!/usr/bin/env node
/**
 * slice.js — Render HTML component files to PNG image slices
 *
 * Usage:
 *   node slice.js --input <file_or_dir> --output <dir> --assets <dir> [options]
 *
 * Options:
 *   --input   <path>    Single HTML file or directory of HTML files (required)
 *   --output  <dir>     Output directory for PNG files (required)
 *   --assets  <dir>     Absolute path to assets folder containing illustration PNGs (required)
 *   --width   <px>      Email width in CSS pixels (default: 600)
 *   --scale   <n>       Device scale factor for retina output (default: 2)
 *   --timeout <ms>      Max wait time per render in ms (default: 10000)
 *   --verbose           Log detailed progress
 *
 * The --assets flag replaces {{ASSETS_BASE}} tokens in template HTML with the
 * absolute path to the assets folder, so Puppeteer can resolve illustration images.
 *
 * Output:
 *   One PNG per input HTML file, named identically (hero-a.html → hero-a.png)
 *   At scale:2 and width:600, output images are 1200px wide (retina-ready)
 *   Height is auto-cropped to exact content height
 *
 * Examples:
 *   node slice.js \
 *     --input ./components/hero-a.html \
 *     --output ./slices/ \
 *     --assets /path/to/email-campaign-builder/references/assets
 *
 *   node slice.js \
 *     --input ./components/ \
 *     --output ./slices/ \
 *     --assets /path/to/email-campaign-builder/references/assets \
 *     --width 600 --scale 2 --verbose
 */

'use strict';

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const args = require('minimist')(process.argv.slice(2));

// ── Config ────────────────────────────────────────────────────────────────────
const INPUT        = args.input;
const OUTPUT       = args.output;
const ASSETS_DIR   = args.assets;
const WIDTH        = parseInt(args.width   || 600,   10);
const SCALE        = parseInt(args.scale   || 2,     10);
const TIMEOUT      = parseInt(args.timeout || 10000, 10);
const VERBOSE      = !!args.verbose;

const ASSETS_TOKEN = '{{ASSETS_BASE}}';

function log(...msg)  { if (VERBOSE) console.log('[slice]', ...msg); }
function info(...msg) { console.log('[slice]', ...msg); }
function err(...msg)  { console.error('[slice] ERROR:', ...msg); }

// ── Validation ────────────────────────────────────────────────────────────────
if (!INPUT || !OUTPUT || !ASSETS_DIR) {
  err('--input, --output, and --assets are required.');
  err('Usage: node slice.js --input <file_or_dir> --output <dir> --assets <dir>');
  process.exit(1);
}

if (!fs.existsSync(INPUT)) {
  err(`Input not found: ${INPUT}`);
  process.exit(1);
}

if (!fs.existsSync(ASSETS_DIR)) {
  err(`Assets directory not found: ${ASSETS_DIR}`);
  process.exit(1);
}

// Resolve assets path to absolute — Puppeteer needs file:// absolute paths
const ASSETS_ABS = `file://${path.resolve(ASSETS_DIR)}`;
log(`Assets path: ${ASSETS_ABS}`);

// Collect HTML files to process
function collectHtmlFiles(inputPath) {
  const stat = fs.statSync(inputPath);
  if (stat.isFile()) {
    if (!inputPath.endsWith('.html')) {
      err(`Input file is not an HTML file: ${inputPath}`);
      process.exit(1);
    }
    return [inputPath];
  }
  return fs.readdirSync(inputPath)
    .filter(f => f.endsWith('.html'))
    .sort()
    .map(f => path.join(inputPath, f));
}

const htmlFiles = collectHtmlFiles(INPUT);

if (htmlFiles.length === 0) {
  err(`No HTML files found in: ${INPUT}`);
  process.exit(1);
}

fs.mkdirSync(OUTPUT, { recursive: true });

// ── Render ────────────────────────────────────────────────────────────────────
async function renderFile(page, htmlFile) {
  const basename = path.basename(htmlFile, '.html');
  const outputFile = path.join(OUTPUT, `${basename}.png`);

  log(`Rendering ${basename}.html...`);

  // Read the template HTML and inject the assets base path
  let html = fs.readFileSync(htmlFile, 'utf8');

  if (html.includes(ASSETS_TOKEN)) {
    html = html.replaceAll(ASSETS_TOKEN, ASSETS_ABS);
    log(`  Injected assets path (${(html.match(/ASSETS_ABS/g) || []).length} replacements)`);
  }

  // Use setContent rather than goto — avoids file:// URL issues with inline content
  // Use a base URL so any remaining relative paths still resolve
  await page.setContent(html, {
    waitUntil: 'networkidle0',
    timeout: TIMEOUT,
  });

  // Wait for fonts to load — critical for Cervanttis, Lust, NeuzeitGro
  await page.evaluate(() => document.fonts.ready);

  // Wait one animation frame to ensure illustrations are painted
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(resolve)));

  // Get exact content height — auto-crops to component, no whitespace
  const contentHeight = await page.evaluate(() => {
    const body = document.body;
    const html = document.documentElement;
    return Math.max(
      body.scrollHeight, body.offsetHeight,
      html.clientHeight, html.scrollHeight, html.offsetHeight
    );
  });

  // Resize viewport to exact content height before screenshotting
  await page.setViewport({
    width: WIDTH,
    height: contentHeight,
    deviceScaleFactor: SCALE,
  });

  await page.screenshot({
    path: outputFile,
    fullPage: true,
    type: 'png',
  });

  const stat = fs.statSync(outputFile);
  info(`✓ ${basename}.png — ${contentHeight}px tall, ${Math.round(stat.size / 1024)}KB`);

  return outputFile;
}

async function main() {
  info(`Processing ${htmlFiles.length} file(s) at ${WIDTH}px × ${SCALE}x scale...`);
  info(`Output   → ${path.resolve(OUTPUT)}`);
  info(`Assets   → ${path.resolve(ASSETS_DIR)}`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--font-render-hinting=none',
      // Allow file:// access to local assets
      '--allow-file-access-from-files',
    ],
  });

  const page = await browser.newPage();

  await page.setViewport({
    width: WIDTH,
    height: 800,
    deviceScaleFactor: SCALE,
  });

  page.setDefaultNavigationTimeout(TIMEOUT);

  const results = [];
  const errors  = [];

  for (const htmlFile of htmlFiles) {
    try {
      const outFile = await renderFile(page, htmlFile);
      results.push(outFile);
    } catch (e) {
      err(`Failed to render ${path.basename(htmlFile)}: ${e.message}`);
      errors.push({ file: htmlFile, error: e.message });
    }
  }

  await browser.close();

  info(`\nDone. ${results.length} slice(s) created, ${errors.length} error(s).`);

  if (errors.length > 0) {
    err('Failed files:');
    errors.forEach(e => err(`  ${path.basename(e.file)}: ${e.error}`));
    process.exit(1);
  }

  // Output JSON manifest for agent parsing
  const manifest = {
    slices: results.map(f => ({
      file: path.basename(f),
      path: path.resolve(f),
      width_css_px: WIDTH,
      scale: SCALE,
      width_actual_px: WIDTH * SCALE,
    })),
  };
  process.stdout.write('\n__SLICE_MANIFEST__\n');
  process.stdout.write(JSON.stringify(manifest, null, 2));
  process.stdout.write('\n__END_MANIFEST__\n');
}

main().catch(e => {
  err(`Fatal: ${e.message}`);
  process.exit(1);
});
