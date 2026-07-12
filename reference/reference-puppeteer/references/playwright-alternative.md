# Playwright Alternative — Full render.js Implementation

Drop-in replacement for Puppeteer-based render.js. Use when Puppeteer can't be installed (missing `unzip`, no root, read-only cache paths).

## Setup

```bash
npm install playwright
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.cache/playwright npx playwright install chromium
```

## render.js (Playwright version)

```js
const path = require('path');
const fs = require('fs');

// MUST be unconditional — shell may have PLAYWRIGHT_BROWSERS_PATH set to a read-only path
process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/data/.cache/playwright';

let playwright;
try {
  playwright = require('playwright');
} catch (e) {
  playwright = null;
}

async function renderToPng(html, opts = {}) {
  if (!playwright) {
    throw new Error('[render] Playwright not installed. Run: npm install playwright && npx playwright install chromium');
  }
  const { outputPath, width = 600, fullPage = true } = opts;
  if (!outputPath) throw new Error('[render] outputPath is required');

  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  const browser = await playwright.chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  try {
    const page = await browser.newPage({ viewport: { width, height: 800 } });
    await page.setContent(html, { waitUntil: 'networkidle' });
    await page.screenshot({ path: outputPath, fullPage, type: 'png' });

    const dimensions = await page.evaluate(() => ({
      width: document.body.scrollWidth,
      height: document.body.scrollHeight
    }));

    return { path: outputPath, size: dimensions };
  } finally {
    await browser.close();
  }
}

async function renderToPdf(html, opts = {}) {
  if (!playwright) {
    throw new Error('[render] Playwright not installed. Run: npm install playwright && npx playwright install chromium');
  }
  const { outputPath, width = 600 } = opts;
  if (!outputPath) throw new Error('[render] outputPath is required');

  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  const browser = await playwright.chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle' });
    await page.pdf({
      path: outputPath,
      width: `${width}px`,
      printBackground: true,
      margin: { top: '0', right: '0', bottom: '0', left: '0' }
    });
    return { path: outputPath };
  } finally {
    await browser.close();
  }
}

function isAvailable() { return !!playwright; }

module.exports = { renderToPng, renderToPdf, isAvailable };
```

## Key differences from Puppeteer render.js

| Puppeteer | Playwright |
|-----------|------------|
| `require('puppeteer')` | `require('playwright')` then `.chromium` |
| `page.setViewport({ width, height })` | `browser.newPage({ viewport: { width, height } })` |
| `waitUntil: 'networkidle0'` | `waitUntil: 'networkidle'` |
| `pdf margin: { top: 0 }` (number) | `pdf margin: { top: '0' }` (string) |
| Bundled Chrome auto-downloads | Chromium must be installed separately via CLI |
| Needs system `unzip` for extraction | Bundles own extraction (no system deps) |
