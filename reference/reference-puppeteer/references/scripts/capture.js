#!/usr/bin/env node
/**
 * capture.js — Screenshot a live URL or local HTML file
 *
 * Usage:
 *   node capture.js --url <url> --output <file> [options]
 *   node capture.js --file <html_file> --output <file> [options]
 *
 * Options:
 *   --url     <url>      Live URL to screenshot (mutually exclusive with --file)
 *   --file    <path>     Local HTML file to screenshot
 *   --output  <path>     Output PNG file path (required)
 *   --width   <px>       Viewport width (default: 1440)
 *   --height  <px>       Viewport height (default: 900). Use 0 for full page height.
 *   --scale   <n>        Device scale factor (default: 1)
 *   --full-page          Capture full scrollable page (default: false)
 *   --wait    <ms>       Additional wait after page load in ms (default: 0)
 *   --selector <css>     Capture a specific element instead of full page
 *   --timeout <ms>       Navigation timeout (default: 15000)
 *
 * Examples:
 *   node capture.js --url https://figandbloom.com --output ./fig-homepage.png --full-page
 *   node capture.js --url https://figandbloom.com --output ./hero.png --selector ".hero-section"
 *   node capture.js --file ./preview.html --output ./preview.png --width 600
 */

'use strict';

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const args = require('minimist')(process.argv.slice(2));

const URL_TARGET = args.url;
const FILE_TARGET = args.file;
const OUTPUT   = args.output;
const WIDTH    = parseInt(args.width   || 1440, 10);
const HEIGHT   = parseInt(args.height  || 900,  10);
const SCALE    = parseInt(args.scale   || 1,    10);
const FULL     = !!(args['full-page'] || args.full_page);
const WAIT     = parseInt(args.wait    || 0,    10);
const SELECTOR = args.selector || null;
const TIMEOUT  = parseInt(args.timeout || 15000, 10);

function err(...msg) { console.error('[capture] ERROR:', ...msg); }
function info(...msg){ console.log('[capture]', ...msg); }

if (!OUTPUT) { err('--output is required'); process.exit(1); }
if (!URL_TARGET && !FILE_TARGET) { err('--url or --file is required'); process.exit(1); }
if (URL_TARGET && FILE_TARGET)   { err('--url and --file are mutually exclusive'); process.exit(1); }

async function main() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT || 900, deviceScaleFactor: SCALE });
  page.setDefaultNavigationTimeout(TIMEOUT);

  const target = URL_TARGET || `file://${path.resolve(FILE_TARGET)}`;
  info(`Loading: ${target}`);

  await page.goto(target, { waitUntil: 'networkidle0', timeout: TIMEOUT });
  await page.evaluate(() => document.fonts.ready);

  if (WAIT > 0) {
    info(`Waiting additional ${WAIT}ms...`);
    await new Promise(r => setTimeout(r, WAIT));
  }

  fs.mkdirSync(path.dirname(path.resolve(OUTPUT)), { recursive: true });

  if (SELECTOR) {
    const element = await page.$(SELECTOR);
    if (!element) { err(`Selector not found: ${SELECTOR}`); await browser.close(); process.exit(1); }
    await element.screenshot({ path: OUTPUT, type: 'png' });
    info(`✓ Element screenshot saved: ${OUTPUT}`);
  } else {
    await page.screenshot({ path: OUTPUT, fullPage: FULL, type: 'png' });
    info(`✓ Screenshot saved: ${OUTPUT} (full-page: ${FULL})`);
  }

  const stat = fs.statSync(OUTPUT);
  info(`  Size: ${Math.round(stat.size / 1024)}KB`);

  await browser.close();
}

main().catch(e => { err(`Fatal: ${e.message}`); process.exit(1); });
