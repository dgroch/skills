#!/usr/bin/env node
/**
 * Reviews.io Gallery API collector (Playwright session-aware).
 *
 * Same as reviewsio_gallery_collector.js but uses Playwright to:
 *  1. Visit the main page (establishes session cookies)
 *  2. Fetches gallery API pages using page.goto() with the session cookie jar
 *  3. Parses the HTML review cards
 *
 * Usage:
 *   node scripts/reviewsio_gallery_collector_pw.js --brand "Daily Blooms" --market National \\
 *     --url "https://www.reviews.io/company-reviews/store/dailyblooms.com.au" \\
 *     --out /tmp/reviewsio.jsonl --max-pages 80
 */

const fs = require('node:fs');
const path = require('node:path');

function stableId(text) {
  const crypto = require('node:crypto');
  return crypto.createHash('sha256').update(String(text)).digest('hex').slice(0, 16);
}

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function usage() {
  console.log(`Usage:
  node scripts/reviewsio_gallery_collector_pw.js \\
    --brand "Daily Blooms" --market National \\
    --url "https://www.reviews.io/company-reviews/store/dailyblooms.com.au" \\
    --out /tmp/reviewsio.jsonl --max-pages 80`);
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const token = argv[i];
    if (!token.startsWith('--')) continue;
    args[token.slice(2)] = argv[++i];
  }
  return args;
}

// ---------------------------------------------------------------------------
// HTML parsing (same as reviewsio_gallery_collector.js)
// ---------------------------------------------------------------------------

function parseGalleryPage(html, context) {
  const records = [];
  
  // Reviews.io gallery: each review is an <a class="list__item list__item--reviewPhoto" href="...">
  // We need to capture the outer <a> href AND the inner content
  // Regex captures: [0] = full match, [1] = href value, [2] = inner content
  const itemRe = /<a\s[^>]*class=["'][^"']*list__item[^"']*["'][^>]*\shref=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  let itemMatch;
  // itemMatch[1] = href, itemMatch[2] = inner content
  while ((itemMatch = itemRe.exec(html)) !== null) {
    const outerHref = itemMatch[1];
    const itemHtml = itemMatch[2];
    const text = itemHtml.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    if (text.length < 20) continue;
    
    if (!/(review|star|flower|delivery|bouquet|blooms|fresh|order|arriv|customer|service|recommend|beautiful|amazing|great|love|disappoint)/i.test(text)) continue;
    
    const reviewer = extractReviewer(itemHtml);
    const rating = extractStars(itemHtml);
    const reviewDate = extractDate(itemHtml);
    const title = extractTitle(itemHtml);
    const body = extractBody(itemHtml);
    
    if (!body || body.length < 10) continue;
    
    const idSeed = `${context.brand}|${context.market}|${context.sourceUrl}|${reviewer || ''}|${reviewDate || ''}|${body.slice(0, 100)}`;
    records.push({
      id: stableId(idSeed),
      brand: context.brand,
      brand_alias: context.brand.toLowerCase().replace(/\s*&\s*/g, '-').replace(/\s+/g, '-'),
      market: context.market,
      source: context.source,
      source_url: context.sourceUrl,
      review_url: outerHref ? ('https://www.reviews.io' + (outerHref.startsWith('/') ? outerHref : '/' + outerHref)) : (extractReviewUrl(itemHtml) || context.sourceUrl),
      reviewer,
      rating,
      review_date: reviewDate,
      collected_at: context.collectedAt || nowIso(),
      title,
      text: body,
      language: 'en',
      status: 'new',
      extraction_method: 'reviewsio_gallery_api_pw',
    });
  }
  
  // Fallback: try div-based review cards
  if (records.length === 0) {
    const divRe = /<div[^>]*class=["'][^"']*(?:review-card|review-item)[^"']*["'][^>]*>([\s\S]*?)<\/div>/gi;
    let divMatch;
    while ((divMatch = divRe.exec(html)) !== null) {
      const itemHtml = divMatch[1];
      const text = itemHtml.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      if (text.length < 20) continue;
      if (!/(review|flower|delivery|bouquet|blooms|order|arriv|customer|service|recommend|beautiful|love)/i.test(text)) continue;
      const reviewer = extractReviewer(itemHtml);
      const rating = extractStars(itemHtml);
      const reviewDate = extractDate(itemHtml);
      const title = extractTitle(itemHtml);
      const body = extractBody(itemHtml);
      if (!body || body.length < 10) continue;
      const idSeed = `${context.brand}|${context.market}|${context.sourceUrl}|${reviewer || ''}|${reviewDate || ''}|${body.slice(0, 100)}`;
      records.push({
        id: stableId(idSeed),
        brand: context.brand,
        brand_alias: context.brand.toLowerCase().replace(/\s*&\s*/g, '-').replace(/\s+/g, '-'),
        market: context.market,
        source: context.source,
        source_url: context.sourceUrl,
        review_url: null,
        reviewer,
        rating,
        review_date: reviewDate,
        collected_at: context.collectedAt || nowIso(),
        title,
        text: body,
        language: 'en',
        status: 'new',
        extraction_method: 'reviewsio_gallery_api_pw',
      });
    }
  }
  
  return records;
}

function extractReviewer(html) {
  const patterns = [
    /class=["'][^"']*(?:author|reviewer|name)[^"']*["'][^>]*>([^<]{2,60})</i,
    /<strong[^>]*>([^<]{2,60})<\/strong>/i,
    /class=["'][^"']*(?:reviewer-name|author-name)[^"']*["'][^>]*>\s*([^<]+)</i,
  ];
  for (const p of patterns) {
    const m = html.match(p);
    if (m) return m[1].replace(/<[^>]+>/g, '').trim().slice(0, 80);
  }
  const m = html.match(/>\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*</);
  if (m) return m[1];
  return null;
}

function extractStars(html) {
  const stars = (html.match(/★/g) || []).length;
  if (stars >= 1 && stars <= 5) return stars;
  const m = html.match(/([0-5](?:\.[0-9])?)\s*(?:out of\s*5|\/\s*5|stars?)/i);
  if (m) { const v = parseFloat(m[1]); if (!isNaN(v)) return v; }
  const dm = html.match(/data-rating=["']?([0-9])/i);
  if (dm) return parseInt(dm[1], 10);
  return null;
}

function extractDate(html) {
  const patterns = [
    /<time[^>]*datetime=["']([^"']+)["']/i,
    /(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})/i,
    /(\d{4}-\d{2}-\d{2})/,
    /([A-Z][a-z]+\s+\d{4})/,
  ];
  for (const p of patterns) {
    const m = html.match(p);
    if (m) return m[1];
  }
  return null;
}

function extractTitle(html) {
  const text = html.replace(/<[^>]+>/g, ' ').trim();
  const m = text.match(/^[""]?([^""\n]{10,120})/);
  return m ? m[1].trim() : null;
}

function extractBody(html) {
  const text = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  if (text.length < 20) return null;
  if (/write\s*(your)?\s*review|review.*template|tell\s*us/i.test(text)) return null;
  return text;
}

function extractReviewUrl(html) {
  // First try from itemHtml itself
  const m = html.match(/href=["']([^"']+)["']/i);
  if (m && m[1].includes('reviews.io')) return 'https://www.reviews.io' + (m[1].startsWith('/') ? m[1] : '/' + m[1]);
  // Also check for data-review-id or similar
  const dataM = html.match(/data-review-id=["']([^"']+)["']/i) || html.match(/data-id=["']([^"']+)["']/i);
  if (dataM) return `https://www.reviews.io/company-review/store/dailyblooms.com.au/${dataM[1]}`;
  return null;
}

function extractStoreId(html) {
  const m = html.match(/["'](\/company-reviews\/gallery\/([a-zA-Z0-9_-]+)\/1)["']/i) ||
    html.match(/gallery\/([a-zA-Z0-9_-]+)\/1/g);
  if (m) return Array.isArray(m) ? m[0].match(/gallery\/([^/]+)\/1/)[1] : m[2] || m[1];
  const dataM = html.match(/data-store-id=["']([^"']+)["']/i) || html.match(/data-gallery-id=["']([^"']+)["']/i);
  if (dataM) return dataM[1];
  return null;
}

function pageHasReviews(html) {
  return /list__item|review-card|review-item|testimonial/i.test(html) && html.length > 200;
}

// ---------------------------------------------------------------------------
// Playwright gallery collector
// ---------------------------------------------------------------------------

async function collectReviewsioPlaywright(url, brand, market, outPath, maxPages) {
  const { chromium } = require('playwright');
  
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 1365, height: 1600 },
    locale: 'en-AU',
    extraHTTPHeaders: { 'Accept-Language': 'en-AU,en;q=0.9' },
  });
  const page = await context.newPage();
  
  // Block noise
  await page.route('**/*', route => {
    const t = route.request().resourceType();
    if (['websocket', 'preflight', 'prefetch', 'media'].includes(t)) { route.abort(); }
    else { route.continue(); }
  });

  console.log(`Loading main page: ${url}`);
  await page.goto(url, { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(3000);
  
  // Extract store ID from the main page HTML
  const mainHtml = await page.content();
  const storeId = extractStoreId(mainHtml);
  if (!storeId) throw new Error('Could not extract store ID');
  console.log(`Store ID: ${storeId}`);
  
  // Intercept the gallery API base URL from the load-more XHR
  let galleryBase = null;
  await page.route('**/*', route => {
    const u = route.request().url();
    if (u.includes('/company-reviews/gallery/') && u.includes(storeId)) {
      galleryBase = u.replace(/\/\d+$/, '/');
    }
    route.continue();
  });
  
  // Trigger one load-more click to capture the gallery URL pattern
  await page.evaluate(() => {
    const el = document.querySelector('[class*="loadmore" i]') ||
               document.querySelector('[class*="LoadMore" i]');
    if (el) { el.scrollIntoView({ block: 'center' }); el.click(); }
  });
  await page.waitForTimeout(3000);
  
  if (!galleryBase) {
    // Fallback: construct from store ID
    galleryBase = `https://www.reviews.io/company-reviews/gallery/${storeId}/`;
    console.log(`Using fallback gallery base: ${galleryBase}`);
  } else {
    console.log(`Gallery base: ${galleryBase}`);
  }
  
  const coll = {
    brand, market, source: 'Reviews.io', sourceUrl: url, collectedAt: nowIso(),
  };
  
  const allRecords = [];
  const seenIds = new Set();
  let consecutiveEmpty = 0;
  
  for (let pageNum = 1; pageNum <= maxPages; pageNum++) {
    const pageUrl = `${galleryBase}${pageNum}`;
    process.stdout.write(`  page ${pageNum}/${maxPages} ...`);
    
    try {
      const resp = await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 20000 });
      const status = resp ? resp.status() : 0;
      await page.waitForTimeout(1500);
      
      if (status !== 200) {
        console.log(` HTTP ${status}`);
        consecutiveEmpty++;
        if (consecutiveEmpty >= 3) { console.log('  Stopping.'); break; }
        continue;
      }
      
      const html = await page.content();
      
      if (!pageHasReviews(html)) {
        console.log(` empty (len=${html.length})`);
        consecutiveEmpty++;
        if (consecutiveEmpty >= 3) { console.log('  Stopping.'); break; }
        continue;
      }
      
      consecutiveEmpty = 0;
      const records = parseGalleryPage(html, coll);
      console.log(` ${records.length} reviews (len=${html.length})`);
      
      for (const r of records) {
        if (!seenIds.has(r.id)) { seenIds.add(r.id); allRecords.push(r); }
      }
    } catch (err) {
      console.error(` ERROR: ${err.message}`);
      consecutiveEmpty++;
      if (consecutiveEmpty >= 3) break;
    }
  }
  
  await browser.close();
  
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, allRecords.map(r => JSON.stringify(r)).join('\n') + '\n', 'utf8');
  console.log(`\nWritten ${allRecords.length} reviews to ${outPath}`);
  return allRecords;
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.brand || !args.market || !args.url || !args.out) { usage(); process.exit(2); }
  const maxPages = parseInt(args['max-pages'] || '80', 10);
  await collectReviewsioPlaywright(args.url, args.brand, args.market, args.out, maxPages);
}

if (require.main === module) main().catch(e => { console.error(e.stack); process.exit(1); });

module.exports = { collectReviewsioPlaywright, parseGalleryPage };
