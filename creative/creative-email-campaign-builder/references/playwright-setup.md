# Playwright Setup for v5 Email Engine

v5 uses Playwright (not Puppeteer) for HTML → PNG/PDF rendering. Playwright is more reliable than Puppeteer in headless Linux environments — it bundles its own extraction logic and doesn't require system `unzip`.

## Installation

```bash
cd v5-engine
npm install playwright
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.cache/playwright npx playwright install chromium
```

## Critical: PLAYWRIGHT_BROWSERS_PATH Must Be Set Unconditionally

The shell environment may already have `PLAYWRIGHT_BROWSERS_PATH` set to a read-only path (e.g. `/opt/hermes/.playwright`). If you use `||` to set it conditionally:

```js
// ❌ WRONG — won't override existing env var
process.env.PLAYWRIGHT_BROWSERS_PATH = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/data/.cache/playwright';
```

Playwright will look for browsers in the wrong location and fail with:
```
Executable doesn't exist at /opt/hermes/.playwright/chromium_headless_shell-...
```

**Correct approach — set unconditionally BEFORE requiring playwright:**

```js
// ✅ CORRECT — always overrides
process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/data/.cache/playwright';
const playwright = require('playwright');
```

This must be the very first thing in `index.js` and `render.js`, before any `require` calls.

## Browser Cache Location

Browsers are cached at `/opt/data/.cache/playwright/` (not the default `/opt/hermes/.playwright` which may be read-only). After installation:

```
/opt/data/.cache/playwright/
├── chromium-1223/
├── chromium_headless_shell-1223/
├── ffmpeg-1011/
└── .links/
```

## Launch Configuration

```js
const browser = await playwright.chromium.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
});
```

All three args are required in containerised/sandboxed environments.

## API Differences from Puppeteer

- `page.setContent(html, { waitUntil: 'networkidle' })` — not `networkidle0`
- `page.screenshot({ path, fullPage, type: 'png' })` — same API
- `page.pdf({ path, width: '600px' })` — same API
- `page.evaluate(() => ...)` — same API
