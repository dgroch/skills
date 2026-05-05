#!/usr/bin/env node
/**
 * Browser-backed review collector for Florist Review Intelligence.
 *
 * Uses Puppeteer to render JavaScript-heavy public review pages, then extracts
 * JSON-LD Review objects and DOM review cards into the same JSONL schema used
 * by review_intel_pipeline.py.
 */

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

function stableId(text) {
  return crypto.createHash('sha256').update(String(text)).digest('hex').slice(0, 16);
}

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function usage() {
  console.log(`Usage:
  node scripts/puppeteer_review_collector.js \\
    --brand "Daily Blooms" --market Melbourne --source Reviews.io \\
    --url "https://www.reviews.io/company-reviews/store/dailyblooms.com.au" \\
    --out /opt/data/florist-review-intelligence/data/raw/browser.jsonl

Options:
  --brand <name>              Required brand name
  --market <market>           Required market/city/cohort
  --source <source>           Source label, e.g. Reviews.io, ProductReview
  --url <url>                 Public review URL to render
  --out <path>                Output JSONL file
  --max-reviews <n>           Max records to output (default: 100)
  --wait-ms <n>               Extra wait after page load (default: 2500)
  --load-more-selector <css>  Optional selector to click repeatedly
  --load-more-clicks <n>      Number of load-more clicks (default: 3)
  --wait-selector <css>       Optional selector to wait for before extraction
  --headful                   Run visible browser for debugging
  --screenshot <path>         Optional screenshot path for evidence/debugging
`);
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const token = argv[i];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    if (key === 'headful') {
      args[key] = true;
    } else {
      args[key] = argv[++i];
    }
  }
  return args;
}

function textFromJsonLd(value) {
  if (value == null) return null;
  if (typeof value === 'string') return value.trim() || null;
  if (typeof value === 'number') return String(value);
  if (Array.isArray(value)) return value.map(textFromJsonLd).filter(Boolean).join(', ') || null;
  if (typeof value === 'object') return textFromJsonLd(value.name || value.text || value['@id']);
  return null;
}

function flattenJsonLd(node, out = []) {
  if (!node) return out;
  if (Array.isArray(node)) {
    for (const item of node) flattenJsonLd(item, out);
    return out;
  }
  if (typeof node !== 'object') return out;
  out.push(node);
  if (Array.isArray(node['@graph'])) flattenJsonLd(node['@graph'], out);
  if (Array.isArray(node.review)) flattenJsonLd(node.review, out);
  if (Array.isArray(node.reviews)) flattenJsonLd(node.reviews, out);
  return out;
}

function isReviewType(value) {
  if (!value) return false;
  const types = Array.isArray(value) ? value : [value];
  return types.map(String).some((t) => /(^|:)Review$/i.test(t) || /^Review$/i.test(t));
}

function extractJsonLdReviewsFromHtml(html, context) {
  const blocks = [];
  const re = /<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let match;
  while ((match = re.exec(html))) blocks.push(match[1]);

  const records = [];
  for (const raw of blocks) {
    let parsed;
    try {
      parsed = JSON.parse(raw.trim());
    } catch (_) {
      continue;
    }
    for (const item of flattenJsonLd(parsed)) {
      if (!isReviewType(item['@type'])) continue;
      const text = textFromJsonLd(item.reviewBody || item.description || item.text);
      if (!text || text.length < 10) continue;
      const ratingRaw = item.reviewRating && (item.reviewRating.ratingValue || item.reviewRating.ratingCount);
      const rating = ratingRaw == null || Number.isNaN(Number(ratingRaw)) ? null : Number(ratingRaw);
      const reviewer = textFromJsonLd(item.author || item.creator || item.publisher);
      const reviewDate = textFromJsonLd(item.datePublished || item.dateCreated);
      const title = textFromJsonLd(item.name || item.headline);
      const idSeed = `${context.brand}|${context.market}|${context.sourceUrl}|${reviewer || ''}|${reviewDate || ''}|${text.slice(0, 120)}`;
      records.push({
        id: stableId(idSeed),
        brand: context.brand,
        brand_alias: context.brand.toLowerCase().replace(/\s*&\s*/g, '-').replace(/\s+/g, '-'),
        market: context.market,
        source: context.source,
        source_url: context.sourceUrl,
        review_url: context.sourceUrl,
        reviewer,
        rating,
        review_date: reviewDate,
        collected_at: context.collectedAt || nowIso(),
        title,
        text,
        language: 'en',
        status: 'new',
        extraction_method: 'puppeteer_jsonld',
      });
    }
  }
  return dedupeRecords(records);
}

function dedupeRecords(records) {
  const seen = new Set();
  const out = [];
  for (const r of records) {
    const key = r.id || stableId(`${r.source_url}|${r.reviewer || ''}|${r.text || ''}`);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(r);
  }
  return out;
}

function resolvePuppeteer() {
  try {
    return require('puppeteer');
  } catch (_) {
    try {
      return require('puppeteer-core');
    } catch (e) {
      throw new Error('Missing Puppeteer. Run `npm install` in the skill directory, or install puppeteer/puppeteer-core globally.');
    }
  }
}

function chromiumPath() {
  const candidates = [
    process.env.CHROMIUM_PATH,
    process.env.PUPPETEER_EXECUTABLE_PATH,
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/google-chrome',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ].filter(Boolean);
  for (const c of candidates) {
    try {
      if (fs.existsSync(c)) return c;
    } catch (_) {}
  }
  return null;
}

async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let total = 0;
      const distance = 600;
      const timer = setInterval(() => {
        window.scrollBy(0, distance);
        total += distance;
        if (total >= document.body.scrollHeight - window.innerHeight || total > 12000) {
          clearInterval(timer);
          resolve();
        }
      }, 150);
    });
  });
}

async function extractDomReviews(page, context, maxReviews) {
  return page.evaluate((ctx, max) => {
    function clean(s) {
      return String(s || '').replace(/\s+/g, ' ').trim();
    }
    function hashSeed(text) {
      // Browser-safe deterministic fallback; Node overwrites IDs if needed.
      let h = 0;
      for (let i = 0; i < text.length; i++) h = Math.imul(31, h) + text.charCodeAt(i) | 0;
      return Math.abs(h).toString(16).padStart(8, '0');
    }
    function ratingFrom(node) {
      const candidates = [
        node.getAttribute('aria-label'),
        node.textContent,
        ...Array.from(node.querySelectorAll('[aria-label*="star" i], [class*="star" i], [class*="rating" i]')).map((n) => n.getAttribute('aria-label') || n.textContent),
      ].filter(Boolean);
      for (const c of candidates) {
        const m = String(c).match(/([0-5](?:\.\d)?)\s*(?:out of\s*5|stars?|\/\s*5)/i);
        if (m) return Number(m[1]);
      }
      return null;
    }
    function reviewerFrom(node) {
      const selectors = ['[class*="author" i]', '[class*="reviewer" i]', '[data-testid*="author" i]', 'strong', 'h3', 'h4'];
      for (const sel of selectors) {
        const el = node.querySelector(sel);
        const t = clean(el && el.textContent);
        if (t && t.length <= 80) return t;
      }
      return null;
    }
    function dateFrom(node) {
      const time = node.querySelector('time[datetime]');
      if (time) return time.getAttribute('datetime');
      const txt = clean(node.textContent);
      const m = txt.match(/\b(\d{1,2}\s+[A-Z][a-z]+\s+\d{4}|[A-Z][a-z]+\s+\d{1,2},\s+\d{4}|\d{4}-\d{2}-\d{2})\b/);
      return m ? m[1] : null;
    }

    const selectors = [
      '[itemtype*="Review" i]',
      '[itemprop="review"]',
      '[data-testid*="review" i]',
      '[class*="review" i]',
      'article',
      'li',
    ];
    const nodes = [];
    for (const sel of selectors) {
      for (const node of document.querySelectorAll(sel)) {
        if (!nodes.includes(node)) nodes.push(node);
      }
    }

    const out = [];
    const seen = new Set();
    for (const node of nodes) {
      const text = clean(node.innerText || node.textContent);
      if (text.length < 40 || text.length > 5000) continue;
      if (!/(review|star|flower|delivery|bouquet|blooms|fresh|ordered|arrived|customer|service|recommend|disappointed|beautiful|late)/i.test(text)) continue;
      const reviewer = reviewerFrom(node);
      const date = dateFrom(node);
      const rating = ratingFrom(node);
      const key = `${reviewer || ''}|${date || ''}|${text.slice(0, 140)}`;
      if (seen.has(key)) continue;
      seen.add(key);
      out.push({
        id: hashSeed(`${ctx.brand}|${ctx.market}|${ctx.sourceUrl}|${key}`),
        brand: ctx.brand,
        brand_alias: ctx.brand.toLowerCase().replace(/\s*&\s*/g, '-').replace(/\s+/g, '-'),
        market: ctx.market,
        source: ctx.source,
        source_url: ctx.sourceUrl,
        review_url: location.href,
        reviewer,
        rating,
        review_date: date,
        collected_at: ctx.collectedAt,
        title: null,
        text,
        language: 'en',
        status: 'new',
        extraction_method: 'puppeteer_dom',
      });
      if (out.length >= max) break;
    }
    return out;
  }, context, maxReviews);
}

async function collectWithPuppeteer(options) {
  const puppeteer = resolvePuppeteer();
  const executablePath = chromiumPath();
  const launchOptions = {
    headless: !options.headful,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  };
  if (executablePath) launchOptions.executablePath = executablePath;

  const browser = await puppeteer.launch(launchOptions);
  const page = await browser.newPage();
  await page.setViewport({ width: 1365, height: 1600, deviceScaleFactor: 1 });
  await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36 FloristReviewBot/1.0');

  const context = {
    brand: options.brand,
    market: options.market,
    source: options.source,
    sourceUrl: options.url,
    collectedAt: nowIso(),
  };

  try {
    await page.goto(options.url, { waitUntil: 'networkidle2', timeout: 45000 });
    if (options.waitSelector) {
      await page.waitForSelector(options.waitSelector, { timeout: 15000 }).catch(() => {});
    }
    if (options.waitMs > 0) await new Promise((r) => setTimeout(r, options.waitMs));

    if (options.loadMoreSelector) {
      for (let i = 0; i < options.loadMoreClicks; i++) {
        const clicked = await page.evaluate((sel) => {
          const el = document.querySelector(sel);
          if (!el) return false;
          el.scrollIntoView({ block: 'center' });
          el.click();
          return true;
        }, options.loadMoreSelector);
        if (!clicked) break;
        await new Promise((r) => setTimeout(r, options.waitMs || 1500));
      }
    }

    await autoScroll(page).catch(() => {});
    if (options.screenshot) {
      fs.mkdirSync(path.dirname(options.screenshot), { recursive: true });
      await page.screenshot({ path: options.screenshot, fullPage: true });
    }

    const html = await page.content();
    const jsonLdRecords = extractJsonLdReviewsFromHtml(html, context);
    const domRecords = await extractDomReviews(page, context, options.maxReviews);
    const combined = dedupeRecords([...jsonLdRecords, ...domRecords]).slice(0, options.maxReviews);

    if (combined.length === 0) {
      return [{
        id: stableId(options.url),
        brand: options.brand,
        brand_alias: options.brand.toLowerCase().replace(/\s*&\s*/g, '-').replace(/\s+/g, '-'),
        market: options.market,
        source: options.source,
        source_url: options.url,
        review_url: null,
        reviewer: null,
        rating: null,
        review_date: null,
        collected_at: context.collectedAt,
        title: null,
        text: '',
        language: 'en',
        status: 'blocked_source',
        reason: 'Puppeteer rendered page but no review-like records were extracted',
        extraction_method: 'puppeteer_no_records',
      }];
    }
    return combined.map((r) => ({ ...r, id: stableId(`${r.brand}|${r.market}|${r.source_url}|${r.reviewer || ''}|${r.review_date || ''}|${r.text || ''}`) }));
  } finally {
    await browser.close();
  }
}

function writeJsonl(records, outPath) {
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, records.map((r) => JSON.stringify(r)).join('\n') + (records.length ? '\n' : ''), 'utf8');
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.brand || !args.market || !args.source || !args.url || !args.out) {
    usage();
    process.exit(args.help ? 0 : 2);
  }
  const options = {
    brand: args.brand,
    market: args.market,
    source: args.source,
    url: args.url,
    out: args.out,
    maxReviews: Number(args['max-reviews'] || 100),
    waitMs: Number(args['wait-ms'] || 2500),
    waitSelector: args['wait-selector'] || null,
    loadMoreSelector: args['load-more-selector'] || null,
    loadMoreClicks: Number(args['load-more-clicks'] || 3),
    headful: Boolean(args.headful),
    screenshot: args.screenshot || null,
  };

  const records = await collectWithPuppeteer(options);
  writeJsonl(records, options.out);
  const statusCounts = records.reduce((acc, r) => {
    acc[r.status] = (acc[r.status] || 0) + 1;
    return acc;
  }, {});
  console.log(JSON.stringify({ out: options.out, records: records.length, status: statusCounts }, null, 2));
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err.stack || String(err));
    process.exit(1);
  });
}

module.exports = {
  stableId,
  extractJsonLdReviewsFromHtml,
  dedupeRecords,
  collectWithPuppeteer,
};
