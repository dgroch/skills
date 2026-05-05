#!/usr/bin/env node
/**
 * firecrawl_collector.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Autonomous ProductReview.com.au collector using Firecrawl's /v0/scrape API.
 *
 * Usage:
 *   node firecrawl_collector.js --sources productreview
 *   node firecrawl_collector.js --sources productreview --dry-run
 *   node firecrawl_collector.js --sources dailyblooms,lvly --limit 5
 *
 * Output:
 *   data/firecrawl/{source}-{YYYY-MM-DD}.jsonl
 *
 * The script is idempotent — run on a cron every 6h. It deduplicates against
 * existing corpus files in data/browser-batch/ and data/firecrawl/.
 *
 * Firecrawl docs: https://docs.firecrawl.dev
 * ProductReview base: https://www.productreview.com.au
 * ─────────────────────────────────────────────────────────────────────────────
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// ── Config ───────────────────────────────────────────────────────────────────

const FIRECRAWL_API_KEY = process.env.FIRECRAWL_API_KEY || '';
const FIRECRAWL_BASE    = 'https://api.firecrawl.dev/v0';

// Fall back to env file if not in environment
function loadApiKey() {
  if (FIRECRAWL_API_KEY) return FIRECRAWL_API_KEY;
  const envPath = path.join(os.homedir(), '.env');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    const match = envContent.match(/FIRECRAWL_API_KEY[=\s]+([^\s\n]+)/);
    if (match) return match[1];
  }
  return null;
}

const API_KEY = loadApiKey();

// ── CLI args ──────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const getArg = (flag, defaultVal) => {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] || defaultVal : defaultVal;
};
const hasFlag = (flag) => args.includes(flag);
const dryRun  = hasFlag('--dry-run');
const limit   = parseInt(getArg('--limit', '9999'), 10);
const sources = getArg('--sources', 'productreview').split(',').map(s => s.trim());
const since   = getArg('--since',   '2020-01-01'); // ISO date filter

// ── Paths ─────────────────────────────────────────────────────────────────────

const SKILL_ROOT = path.resolve(__dirname, '..');
const DATA_DIR   = path.join(SKILL_ROOT, 'data', 'firecrawl');
const BATCH_DIR  = path.join(SKILL_ROOT, 'data', 'browser-batch');

// Ensure output dir
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

const today = new Date().toISOString().slice(0, 10);

// ── Logging ───────────────────────────────────────────────────────────────────

const log = (level, msg) => console.log(`[${new Date().toISOString()}] [${level}] ${msg}`);
const info  = (msg) => log('INFO',  msg);
const warn  = (msg) => log('WARN',  msg);
const error = (msg) => log('ERROR', msg);

// ── HTTP helper ───────────────────────────────────────────────────────────────

async function firecrawlScrape(url, opts = {}) {
  if (!API_KEY) throw new Error('FIRECRAWL_API_KEY not found in env or ~/.env');

  const payload = {
    url,
    // Don't use LLM extraction — raw HTML with structured prompt is faster/cheaper
    pageOptions: { onlyMainContent: true },
    // Use markdown extraction (fast, no LLM cost)
    extractOptions: opts.extractOptions || {
      prompt: `Extract all customer reviews from this page. For each review return: reviewer name, star rating (1-5), review date/relative time (e.g. "2w ago"), review text body, and the product/service reviewed. Return as JSON array.`
    }
  };

  // Allow caller to override extractOptions for simple pagination (no LLM needed)
  if (opts.skipExtract) delete payload.extractOptions;

  const res = await fetch(`${FIRECRAWL_BASE}/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Firecrawl ${res.status} on ${url}: ${text.slice(0, 200)}`);
  }

  return res.json();
}

// ── ProductReview.com.au ──────────────────────────────────────────────────────
//
// ProductReview paginates listings at:
//   https://www.productreview.com.au/listings/{slug}?page=N
//   (or simply /listings/{slug}?page=N for subsequent pages)
//
// The category listing page lives at:
//   https://www.productreview.com.au/c/flower-gift-shops
//
// Strategy:
//   1. Fetch category page to get brand slugs
//   2. For each slug, scrape listing page (with review pagination)
//   3. Extract reviews via regex from raw markdown — NO LLM call
//      (Reviews appear in structured blocks in the HTML/markdown)
//
// ─────────────────────────────────────────────────────────────────────────────

const PR_BASE = 'https://www.productreview.com.au';

// Known competitor slugs for florists (pre-seeded to avoid always scraping category page)
const FLORIST_SLUGS = [
  'daily-blooms',
  'lvly',
  'fig-and-bloom',
  'roses-only',
  'sarah-s-flowers',
  'bloomeroo',
  '1300-flowers',
  'freshflowers-com-au',
  'easy-flowers',
  'flowers-across-melbourne',
  'flowers-across-sydney',
  'flowers-across-brisbane',
  'a-little-luxury',
  'edible-blooms',
  'gifts-australia',
];

/**
 * Extract reviews from raw ProductReview markdown/text.
 * Reviews appear as repeating blocks like:
 *   ★★★★★ — reviewerName · 2w ago
 *   Review text goes here...
 *
 * Returns array of review objects.
 */
function extractReviewsFromText(text, source) {
  const reviews = [];
  
  // Pattern: star rating + reviewer + relative time + review body
  // e.g. "★★★★★ — Sarah · 3w ago\nGreat flowers..."
  // Also handles: "★★★★☆" (4 stars)
  const blockRe = /([★☆]{1,5})\s*[—\-–]\s*([^\n]+?)\s*[·•]\s*(\d+\w+\s+ago|[^\n]+?)\n([\s\S?]+?)(?=(?:[★☆]{1,5}\s*[—\-–])|$)/g;
  
  let match;
  while ((match = blockRe.exec(text)) !== null) {
    const starsStr = match[1];
    const reviewer  = match[2].trim();
    const time      = match[3].trim();
    const body      = match[4].trim();

    // Parse star rating
    const filled = (starsStr.match(/★/g) || []).length;
    const empty  = (starsStr.match(/☆/g) || []).length;
    const rating = filled + (empty > 0 ? 0.5 : 0);

    if (body.length < 10) continue; // Skip garbage matches

    reviews.push({
      id: `pr-${source}-${Buffer.from(`${reviewer}${time}${body}`.slice(0, 80)).toString('hex')}`,
      source: 'productreview',
      brand: source,
      reviewer: reviewer.slice(0, 100),
      rating,
      time,
      text: body.slice(0, 2000),
      url: `${PR_BASE}/listings/${source}`,
      date_collected: today,
      sentiment: rating >= 4 ? 'positive' : rating === 3 ? 'mixed' : 'negative'
    });
  }

  return reviews;
}

/**
 * Scrape a ProductReview listing page and extract reviews.
 * Uses simple regex on markdown — no LLM call.
 */
async function scrapePrListing(slug, pageNum = 1) {
  const url = pageNum === 1
    ? `${PR_BASE}/listings/${slug}`
    : `${PR_BASE}/listings/${slug}?page=${pageNum}`;

  info(`Fetching ${url}`);

  // Use skipExtract=true to get raw markdown without LLM processing
  // Then parse reviews with regex — much faster and free
  let data;
  try {
    data = await firecrawlScrape(url, { skipExtract: true });
  } catch (err) {
    warn(`Failed to fetch ${url}: ${err.message}`);
    return { reviews: [], hasMore: false, error: err.message };
  }

  // Extract markdown from response
  const md = data.data?.markdown || data.data || '';

  // Try to find pagination indicator in the text
  // ProductReview shows "Showing X-Y of Z reviews"
  const totalMatch = md.match(/of\s+([\d,]+)\s+reviews/i);
  const total = totalMatch ? parseInt(totalMatch[1].replace(',', ''), 10) : 0;

  // Find current page range
  const rangeMatch = md.match(/Showing\s+(\d+)[-\s]+(\d+)/i);
  const currentEnd = rangeMatch ? parseInt(rangeMatch[2], 10) : 0;

  const hasMore = total > currentEnd;

  const reviews = extractReviewsFromText(md, slug);

  return { reviews, hasMore, total, currentEnd };
}

/**
 * Scrape all pages for a given ProductReview listing.
 * Stops when pagination runs out or maxPages reached.
 */
async function scrapePrListingFull(slug, maxPages = 10) {
  const allReviews = [];

  for (let page = 1; page <= maxPages; page++) {
    const { reviews, hasMore, total } = await scrapePrListing(slug, page);
    
    if (reviews.length === 0) {
      info(`  Page ${page}: no reviews found, stopping.`);
      break;
    }

    allReviews.push(...reviews);
    info(`  Page ${page}: +${reviews.length} reviews (total so far: ${allReviews.length}${total ? ` / ~${total}` : ''})`);

    if (!hasMore) break;

    // Polite delay between pages
    await new Promise(r => setTimeout(r, 500));
  }

  return allReviews;
}

/**
 * Fetch the category page to discover new brand slugs.
 */
async function discoverBrandSlugs() {
  const url = `${PR_BASE}/c/flower-gift-shops`;
  info(`Discovering brand slugs from ${url}`);

  try {
    const data = await firecrawlScrape(url, { skipExtract: true });
    const md = data.data?.markdown || '';

    // Extract slugs from listing URLs in the markdown
    // Pattern: /listings/brand-slug or /l/brand-slug
    const slugSet = new Set(FLORIST_SLUGS); // keep pre-seeded
    const slugRe  = /\/(?:listings|l)\/([a-z0-9-]+)/gi;
    let match;
    while ((match = slugRe.exec(md)) !== null) {
      slugSet.add(match[1].toLowerCase());
    }

    return [...slugSet];
  } catch (err) {
    warn(`Category discovery failed: ${err.message}. Using pre-seeded slugs.`);
    return FLORIST_SLUGS;
  }
}

// ── Reviews.io fallback ───────────────────────────────────────────────────────
//
// If Firecrawl is pointed at Reviews.io gallery pages, we can also do
// simple HTTP fetches without LLM — the gallery API is just HTML.
// This keeps Firecrawl credits free for ProductReview which has no API.
//
// ─────────────────────────────────────────────────────────────────────────────

async function fetchReviewsIoGalleryPage(storeId, page) {
  const url = `https://www.reviews.io/company-reviews/gallery/${storeId}/${page}`;
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; PR-Collector/1.0)' }
  });

  if (!res.ok) throw new Error(`Reviews.io ${res.status}`);
  
  const html = await res.text();

  // Parse: <a class="list__item" href="..."> ... <blockquote>...</blockquote> </a>
  const reviews = [];
  const itemRe  = /<a class="list__item" href="([^"]+)">([\s\S]*?)<\/a>/gi;
  let m;
  while ((m = itemRe.exec(html)) !== null) {
    const href   = m[1];
    const inside = m[2];

    // Extract star rating
    const starsMatch = inside.match(/([★☆]{1,5})/);
    const stars = starsMatch ? (starsMatch[1].match(/★/g) || []).length : 0;

    // Extract reviewer and date
    const metaMatch = inside.match(/<cite[^>]*>([^<]+)<\/cite>/);
    const dateMatch = inside.match(/(\d+\s+\w+\s+\d{4}|\w+\s+\d{4})/);

    // Extract review text
    const blockRe = /<blockquote[^>]*>([\s\S]*?)<\/blockquote>/i;
    const blockMatch = inside.match(blockRe);
    const text = blockMatch ? blockMatch[1].replace(/<[^>]+>/g, '').trim() : '';

    const reviewer = metaMatch ? metaMatch[1].trim() : 'Anonymous';

    reviews.push({
      id: `rio-${storeId}-${Buffer.from(href).toString('hex').slice(0, 12)}`,
      source: 'reviews.io',
      brand: storeId.replace('-com-au', ''),
      reviewer,
      rating: stars,
      time: dateMatch ? dateMatch[1] : '',
      text: text.slice(0, 2000),
      url: href,
      date_collected: today,
      sentiment: stars >= 4 ? 'positive' : stars === 3 ? 'mixed' : 'negative'
    });
  }

  return reviews;
}

// ── Deduplication ─────────────────────────────────────────────────────────────

/**
 * Load existing review IDs from all JSONL files under data/.
 * Returns a Set of known IDs.
 */
function loadExistingIds() {
  const ids = new Set();
  const dirs = [DATA_DIR, BATCH_DIR];

  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    for (const file of fs.readdirSync(dir)) {
      if (!file.endsWith('.jsonl')) continue;
      const content = fs.readFileSync(path.join(dir, file), 'utf8');
      for (const line of content.split('\n')) {
        if (!line.trim()) continue;
        try {
          const rec = JSON.parse(line);
          if (rec.id) ids.add(rec.id);
        } catch (_) {}
      }
    }
  }

  return ids;
}

// ── Write output ─────────────────────────────────────────────────────────────

function writeReviews(reviews, source) {
  if (reviews.length === 0) return 0;

  const outPath = path.join(DATA_DIR, `${source}-${today}.jsonl`);
  const lines = reviews.map(r => JSON.stringify(r)).join('\n') + '\n';

  const exists = fs.existsSync(outPath);
  fs.appendFileSync(outPath, lines);
  info(`Wrote ${reviews.length} reviews to ${path.basename(outPath)}${exists ? ' (appended)' : ''}`);

  return reviews.length;
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  if (!API_KEY) {
    error('FIRECRAWL_API_KEY not set. Check ~/.env or environment.');
    process.exit(1);
  }

  info(`Firecrawl collector starting — sources: ${sources.join(', ')}`);
  info(`Dry run: ${dryRun} | Limit: ${limit}`);

  const existingIds = loadExistingIds();
  info(`Loaded ${existingIds.size} existing review IDs for dedup`);

  let totalWritten = 0;

  for (const source of sources) {
    if (totalWritten >= limit) break;

    info(`\n══ Processing source: ${source} ══`);

    try {
      let slugs = [];

      if (source === 'productreview') {
        // Discover slugs from category page (skip in dry run)
        slugs = dryRun ? FLORIST_SLUGS.slice(0, 3) : await discoverBrandSlugs();
        info(`Found ${slugs.length} brand slugs`);
      } else if (source === 'reviews.io') {
        slugs = ['dailyblooms-com-au', 'lvly-com-au'];
      }

      for (const slug of slugs) {
        if (totalWritten >= limit) break;

        let reviews = [];

        if (source === 'productreview') {
          reviews = await scrapePrListingFull(slug, 10);
        } else if (source === 'reviews.io') {
          // Use direct HTTP for Reviews.io gallery — no Firecrawl credits needed
          for (let page = 1; page <= 50; page++) {
            const pageReviews = await fetchReviewsIoGalleryPage(slug, page);
            if (pageReviews.length === 0) break;
            reviews.push(...pageReviews);
            info(`  ${slug} page ${page}: +${pageReviews.length} (total: ${reviews.length})`);
            await new Promise(r => setTimeout(r, 300));
          }
        }

        // Deduplicate
        const newReviews = reviews.filter(r => !existingIds.has(r.id));
        newReviews.forEach(r => existingIds.add(r.id)); // prevent cross-page dups

        info(`  ${slug}: ${reviews.length} collected, ${newReviews.length} new`);

        if (!dryRun) {
          const written = writeReviews(newReviews, `${source}-${slug}`);
          totalWritten += written;
        }

        await new Promise(r => setTimeout(r, 800)); // polite delay between slugs
      }
    } catch (err) {
      error(`Source ${source} failed: ${err.message}`);
    }
  }

  info(`\nDone. Total new reviews written: ${totalWritten}`);
  info(`Output directory: ${DATA_DIR}`);

  process.exit(0);
}

main().catch(err => {
  error(`Fatal: ${err.message}`);
  process.exit(1);
});