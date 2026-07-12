/**
 * v5-engine: render.js
 *
 * Playwright-based HTML → image/PDF rendering.
 * Used for visual QA and Klaviyo CODE-mode image upload.
 */

const path = require('path');
const fs = require('fs');

// Set browser cache path before loading playwright
process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/data/.cache/playwright';

let playwright;
try {
  playwright = require('playwright');
} catch (e) {
  playwright = null;
}

/**
 * Render HTML to PNG screenshot
 *
 * @param {string} html - Full HTML string
 * @param {object} opts
 * @param {string} opts.outputPath - Where to save the PNG
 * @param {number} opts.width - Viewport width (default: 600)
 * @param {boolean} opts.fullPage - Capture full page (default: true)
 * @returns {Promise<{ path: string, size: { width, height } }>}
 */
async function renderToPng(html, opts = {}) {
  if (!playwright) {
    throw new Error('[render] Playwright not installed. Run: npm install playwright && npx playwright install chromium');
  }

  const {
    outputPath,
    width = 600,
    fullPage = true
  } = opts;

  if (!outputPath) {
    throw new Error('[render] outputPath is required');
  }

  // Ensure output directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const browser = await playwright.chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  try {
    const page = await browser.newPage({
      viewport: { width, height: 800 }
    });

    await page.setContent(html, { waitUntil: 'networkidle' });

    await page.screenshot({
      path: outputPath,
      fullPage,
      type: 'png'
    });

    // Get dimensions
    const dimensions = await page.evaluate(() => ({
      width: document.body.scrollWidth,
      height: document.body.scrollHeight
    }));

    return {
      path: outputPath,
      size: dimensions
    };
  } finally {
    await browser.close();
  }
}

/**
 * Render HTML to PDF
 *
 * @param {string} html - Full HTML string
 * @param {object} opts
 * @param {string} opts.outputPath - Where to save the PDF
 * @param {number} opts.width - Page width in px (default: 600)
 * @returns {Promise<{ path: string }>}
 */
async function renderToPdf(html, opts = {}) {
  if (!playwright) {
    throw new Error('[render] Playwright not installed. Run: npm install playwright && npx playwright install chromium');
  }

  const {
    outputPath,
    width = 600
  } = opts;

  if (!outputPath) {
    throw new Error('[render] outputPath is required');
  }

  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

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

/**
 * Check if Playwright is available
 */
function isAvailable() {
  return !!playwright;
}

module.exports = { renderToPng, renderToPdf, isAvailable };
