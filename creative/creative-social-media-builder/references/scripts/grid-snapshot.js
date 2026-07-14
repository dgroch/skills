#!/usr/bin/env node
/**
 * grid-snapshot.js — Best-effort screenshot of an Instagram profile grid, for
 * planning a row of 3 against the current top of the grid (SKILL "Row" mode).
 * Reuses the `puppeteer` skill's installed Chromium, same as render.js.
 *
 * Usage:
 *   node grid-snapshot.js --handle figandbloom --output /tmp/grid.png
 *
 * Options:
 *   --handle    <name>   Instagram handle (no @). Required.
 *   --output    <path>   Output PNG path. Default ./grid-<handle>.png
 *   --full-page          Capture the full page instead of the first viewport.
 *   --timeout   <ms>     Navigation timeout. Default 45000.
 *   --puppeteer <path>   Path to a node_modules dir that has puppeteer.
 *   --verbose            Log progress.
 *
 * Emits a __GRID_MANIFEST__ … __END_MANIFEST__ JSON block on stdout:
 *   { ok, handle, output, gated, notes[] }
 *
 * IMPORTANT: Instagram frequently login-walls logged-out views. This script is
 * best-effort by design — it detects the login wall and reports gated:true
 * rather than pretending success. When gated, fall back to asking the user for
 * a screenshot of their grid (the reliable path — see operating-instructions.md,
 * "Mode B — Row"). Do not attempt to log in or bypass the wall.
 */
'use strict';

const fs = require('fs');
const path = require('path');

(function addDepPaths() {
  const here = __dirname;
  const candidates = [
    process.env.PUPPETEER_SKILL_NODE_MODULES,
    path.join(here, '..', '..', '..', '..', 'reference', 'reference-puppeteer', 'references', 'node_modules'),
    path.join(here, '..', 'node_modules'),
  ].filter(Boolean);
  for (const c of candidates) { if (fs.existsSync(c) && !module.paths.includes(c)) module.paths.unshift(c); }
})();

const args = require('minimist')(process.argv.slice(2), { boolean: ['full-page', 'verbose'] });

function info(...m) { if (args.verbose) console.log('[grid]', ...m); }
function fail(...m) { console.error('[grid] ERROR:', ...m); process.exit(1); }

function loadPuppeteer() {
  const candidates = [];
  if (args.puppeteer) candidates.push(path.resolve(args.puppeteer, 'puppeteer'));
  candidates.push('puppeteer');
  candidates.push(path.join(__dirname, '..', '..', '..', '..', 'reference', 'reference-puppeteer', 'references', 'node_modules', 'puppeteer'));
  for (const c of candidates) {
    try { return require(c); } catch (_) { /* try next */ }
  }
  fail('Could not require puppeteer. Run `npm install` in reference-puppeteer/references, or pass --puppeteer <node_modules path>.');
}

(async () => {
  const handle = String(args.handle || '').replace(/^@/, '');
  if (!handle) fail('--handle is required (Instagram handle, no @).');
  const output = path.resolve(args.output || `grid-${handle}.png`);
  const timeout = parseInt(args.timeout || 45000, 10);
  const url = `https://www.instagram.com/${encodeURIComponent(handle)}/`;
  const notes = [];

  const puppeteer = loadPuppeteer();
  info('launching Chromium');
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  let gated = false;
  try {
    const page = await browser.newPage();
    // Desktop viewport wide enough that the grid renders 3-up at a readable size.
    await page.setViewport({ width: 1280, height: 1600, deviceScaleFactor: 1 });
    info('navigating to', url);
    await page.goto(url, { waitUntil: 'networkidle2', timeout });
    // Let lazy-loaded grid thumbnails settle.
    await new Promise(r => setTimeout(r, 3000));

    gated = await page.evaluate(() => {
      const text = document.body ? document.body.innerText : '';
      const loginWall = /log in|sign up/i.test(text) && !!document.querySelector('input[name="username"], form[id*="login"]');
      const hasGrid = document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]').length >= 3;
      return loginWall || !hasGrid;
    });
    if (gated) notes.push('Login wall or empty grid detected — screenshot saved for inspection, but treat grid state as UNKNOWN and ask the user for a screenshot instead.');

    await page.screenshot({ path: output, fullPage: !!args['full-page'] });
    info('saved', output);
  } finally {
    await browser.close();
  }

  const manifest = { ok: !gated, handle, output, gated, notes };
  console.log('__GRID_MANIFEST__');
  console.log(JSON.stringify(manifest, null, 2));
  console.log('__END_MANIFEST__');
  process.exit(gated ? 2 : 0);
})().catch(e => fail(e.message));
