#!/usr/bin/env node
/**
 * pdf.js — Render an HTML file to PDF
 *
 * Usage:
 *   node pdf.js --input <html_file> --output <pdf_file> [options]
 *
 * Options:
 *   --input   <path>     HTML file to render (required)
 *   --output  <path>     Output PDF file path (required)
 *   --format  <size>     Page size: A4, Letter, A3, etc. (default: A4)
 *   --margin  <px>       Uniform page margin in px (default: 40)
 *   --landscape          Render in landscape orientation
 *   --no-background      Omit background colours/images (default: backgrounds included)
 *   --timeout <ms>       Navigation timeout (default: 15000)
 *
 * Examples:
 *   node pdf.js --input ./report.html --output ./report.pdf
 *   node pdf.js --input ./invoice.html --output ./invoice.pdf --format A4 --margin 48
 *   node pdf.js --input ./wide-report.html --output ./wide.pdf --landscape
 */

'use strict';

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const args = require('minimist')(process.argv.slice(2));

const INPUT     = args.input;
const OUTPUT    = args.output;
const FORMAT    = args.format    || 'A4';
const MARGIN    = parseInt(args.margin || 40, 10);
const LANDSCAPE = !!args.landscape;
const NO_BG     = !!args['no-background'];
const TIMEOUT   = parseInt(args.timeout || 15000, 10);

function err(...msg)  { console.error('[pdf] ERROR:', ...msg); }
function info(...msg) { console.log('[pdf]', ...msg); }

if (!INPUT)  { err('--input is required');  process.exit(1); }
if (!OUTPUT) { err('--output is required'); process.exit(1); }
if (!fs.existsSync(INPUT)) { err(`File not found: ${INPUT}`); process.exit(1); }

async function main() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });

  const page = await browser.newPage();
  page.setDefaultNavigationTimeout(TIMEOUT);

  const fileUrl = `file://${path.resolve(INPUT)}`;
  info(`Loading: ${fileUrl}`);
  await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: TIMEOUT });
  await page.evaluate(() => document.fonts.ready);

  fs.mkdirSync(path.dirname(path.resolve(OUTPUT)), { recursive: true });

  const marginStr = `${MARGIN}px`;
  await page.pdf({
    path: OUTPUT,
    format: FORMAT,
    landscape: LANDSCAPE,
    printBackground: !NO_BG,
    margin: { top: marginStr, right: marginStr, bottom: marginStr, left: marginStr },
  });

  const stat = fs.statSync(OUTPUT);
  info(`✓ PDF saved: ${OUTPUT} — ${Math.round(stat.size / 1024)}KB`);

  await browser.close();
}

main().catch(e => { err(`Fatal: ${e.message}`); process.exit(1); });
