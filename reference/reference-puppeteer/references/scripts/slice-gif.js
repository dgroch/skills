#!/usr/bin/env node
/**
 * slice-gif.js — Render an ordered sequence of HTML "frame" files to ONE animated GIF.
 *
 * Companion to slice.js. Where slice.js rasterises a designed block to a static PNG,
 * slice-gif.js rasterises an ANIMATED HERO: N frame states of the SAME 600px block,
 * each a standalone HTML file (shell-wrapped, tokens filled, {{ASSETS_BASE}} resolved),
 * captured at identical dimensions and encoded into a single looping GIF.
 *
 * The Fig & Bloom corpus animates heroes three ways (see references/research/freq.json):
 *   - reveal mechanics (flower-of-the-month / product reveals)  → 2–4 frames
 *   - UGC / review photo carousels                              → 8–18 frames
 *   - sale / urgency flashes                                    → 4–5 frames
 * Each "frame" is just the block with a different photo / label / colour state.
 *
 * Usage:
 *   node slice-gif.js --frames <dir> --output <file.gif> --assets <dir> [options]
 *
 * Options:
 *   --frames  <dir>   Directory of frame HTML files. Rendered in SORTED filename order
 *                     (name them frame-00.html, frame-01.html, …). (required)
 *   --output  <file>  Output .gif path. (required)
 *   --assets  <dir>   Absolute path to the illustration assets folder ({{ASSETS_BASE}}). (required)
 *   --width   <px>    Email width in CSS pixels (default: 600)
 *   --scale   <n>     Device scale factor (default: 1 — GIF heroes ship at 1x to keep file size
 *                     reasonable for email; bump to 2 only for short heroes)
 *   --delay   <ms>    Per-frame delay in ms (default: 600)
 *   --loop    <n>     0 = loop forever (default), -1 = play once
 *   --timeout <ms>    Max wait per frame (default: 30000)
 *   --verbose
 *
 * Output: one animated GIF. All frames are clipped to the height of the FIRST frame, so author
 * every frame to the same content height. Prints a __GIF_MANIFEST__ JSON block to stdout.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const puppeteer = require('puppeteer');
const { PNG } = require('pngjs');
const { GIFEncoder, quantize, applyPalette } = require('gifenc');
const argv = require('minimist')(process.argv.slice(2));

function die(msg) { console.error('slice-gif: ' + msg); process.exit(1); }

const framesDir = argv.frames;
const output = argv.output;
const assets = argv.assets;
const width = parseInt(argv.width || '600', 10);
const scale = parseInt(argv.scale || '1', 10);
const delay = parseInt(argv.delay || '600', 10);
const loop = (argv.loop === undefined) ? 0 : parseInt(argv.loop, 10);
const timeout = parseInt(argv.timeout || '30000', 10);
const verbose = !!argv.verbose;

if (!framesDir || !output || !assets) die('--frames, --output and --assets are required');
if (!fs.existsSync(framesDir)) die('frames dir not found: ' + framesDir);

const frameFiles = fs.readdirSync(framesDir)
  .filter(f => /\.html?$/i.test(f))
  .sort()
  .map(f => path.join(framesDir, f));
if (frameFiles.length < 2) die('need at least 2 frame HTML files in ' + framesDir);

const ASSETS = path.resolve(assets).replace(/\\/g, '/');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
    protocolTimeout: Math.max(timeout * 4, 120000),
  });
  let gifW = null, gifH = null;
  const enc = GIFEncoder();
  const page = await browser.newPage();
  await page.setViewport({ width, height: 800, deviceScaleFactor: scale });

  for (let i = 0; i < frameFiles.length; i++) {
    let html = fs.readFileSync(frameFiles[i], 'utf8').split('{{ASSETS_BASE}}').join('file://' + ASSETS);
    // 'load' fires only after every <img> has loaded, so images are ready here.
    await page.setContent(html, { waitUntil: 'load', timeout });
    await page.evaluate(() => (document.fonts && document.fonts.ready) ? document.fonts.ready : null).catch(() => {});
    await new Promise(r => setTimeout(r, 200)); // settle fonts/layout
    // measure full content height on the first frame, lock it for all frames
    if (i === 0) {
      const h = await page.evaluate(() => document.body.scrollHeight);
      gifW = width * scale;
      gifH = h * scale;
    }
    const buf = await page.screenshot({ clip: { x: 0, y: 0, width, height: gifH / scale }, type: 'png' });
    const png = PNG.sync.read(buf);
    const rgba = new Uint8Array(png.data);
    const palette = quantize(rgba, 256);
    const index = applyPalette(rgba, palette);
    enc.writeFrame(index, png.width, png.height, { palette, delay, repeat: loop });
    if (verbose) console.error(`  frame ${i + 1}/${frameFiles.length}: ${path.basename(frameFiles[i])} ${png.width}x${png.height}`);
  }
  enc.finish();
  await browser.close();

  fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
  fs.writeFileSync(output, Buffer.from(enc.bytes()));
  const bytes = fs.statSync(output).size;

  console.log('__GIF_MANIFEST__' + JSON.stringify({
    output: path.resolve(output),
    frames: frameFiles.length,
    width_actual_px: gifW,
    height_actual_px: gifH,
    delay_ms: delay,
    loop,
    bytes,
  }, null, 2) + '__END_MANIFEST__');
})().catch(e => { console.error(e); process.exit(1); });
