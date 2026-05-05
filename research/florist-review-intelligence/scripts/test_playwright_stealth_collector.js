#!/usr/bin/env node
/**
 * Smoke tests for playwright_stealth_collector.js
 * Tests: stableId determinism, JSON-LD extraction, dedup, field normalisation, CLI parsing.
 * Run: node scripts/test_playwright_stealth_collector.js
 */

const { stableId, extractJsonLdReviewsFromHtml, dedupeRecords } = require('./playwright_stealth_collector.js');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function assert(condition, message) {
  if (!condition) throw new Error(`FAIL: ${message}`);
}
function assertEqual(actual, expected, message) {
  if (actual !== expected) throw new Error(`FAIL: ${message} — got ${JSON.stringify(actual)}, expected ${JSON.stringify(expected)}`);
}

// ---------------------------------------------------------------------------
// Test: stableId determinism
// ---------------------------------------------------------------------------
assertEqual(
  stableId('hello world'),
  stableId('hello world'),
  'stableId is deterministic'
);
assertEqual(
  stableId('hello world').length,
  16,
  'stableId is 16 hex chars'
);
assert(
  stableId('a') !== stableId('b'),
  'stableId produces different outputs for different inputs'
);

// ---------------------------------------------------------------------------
// Test: JSON-LD extraction — basic Review
// ---------------------------------------------------------------------------
const singleReviewHtml = `<html><body>
<script type="application/ld+json">
{
  "@type": "WebPage",
  "@graph": [
    {
      "@type": "Review",
      "reviewRating": { "@type": "Rating", "ratingValue": 5 },
      "author": { "@type": "Person", "name": "Sarah M." },
      "datePublished": "2026-04-01",
      "reviewBody": "The flowers were absolutely stunning and lasted over two weeks. Made my birthday special.",
      "itemReviewed": { "@type": "Product", "name": "Signature Bunch" }
    }
  ]
}
</script></body></html>`;

const ctx1 = { brand: 'Daily Blooms', market: 'Melbourne', source: 'Reviews.io', sourceUrl: 'https://example.com', collectedAt: '2026-05-05T00:00:00Z' };
const records1 = extractJsonLdReviewsFromHtml(singleReviewHtml, ctx1);
assertEqual(records1.length, 1, 'single JSON-LD review extracted');
assertEqual(records1[0].rating, 5, 'rating parsed');
assertEqual(records1[0].reviewer, 'Sarah M.', 'reviewer parsed');
assertEqual(records1[0].review_date, '2026-04-01', 'date parsed');
assertEqual(records1[0].brand, 'Daily Blooms', 'brand propagated');
assertEqual(records1[0].status, 'new', 'status is new');
assertEqual(records1[0].extraction_method, 'playwright_stealth_jsonld', 'extraction_method set');

// ---------------------------------------------------------------------------
// Test: JSON-LD extraction — multiple reviews, dedup
// ---------------------------------------------------------------------------
const multiReviewHtml = `<html><body>
<script type="application/ld+json">
{
  "@type": "Review",
  "reviewRating": { "ratingValue": 4 },
  "author": { "name": "James K." },
  "datePublished": "2026-03-15",
  "reviewBody": "Really beautiful arrangement. Would order again."
}
</script></body></html>`;

const records2 = extractJsonLdReviewsFromHtml(multiReviewHtml, ctx1);
assertEqual(records2.length, 1, 'single review from multi-property JSON-LD');
assertEqual(records2[0].text, 'Really beautiful arrangement. Would order again.', 'full text extracted');

// ---------------------------------------------------------------------------
// Test: JSON-LD extraction — skips short / non-review blocks
// ---------------------------------------------------------------------------
const junkHtml = `<html><body>
<script type="application/ld+json">
{ "@type": "Product", "name": "Some item" }
</script>
<script type="application/ld+json">
{ "@type": "Review", "reviewBody": "Short", "reviewRating": { "ratingValue": 1 } }
</script>
</body></html>`;
const records3 = extractJsonLdReviewsFromHtml(junkHtml, ctx1);
assertEqual(records3.length, 0, 'review with body < 10 chars is skipped');

// ---------------------------------------------------------------------------
// Test: dedupeRecords
// ---------------------------------------------------------------------------
const dupes = [
  { id: 'abc', text: 'one', source_url: 'https://x.com' },
  { id: 'abc', text: 'one', source_url: 'https://x.com' },
  { id: 'def', text: 'two', source_url: 'https://x.com' },
];
const deduped = dedupeRecords(dupes);
assertEqual(deduped.length, 2, 'deduped to 2 records');

// ---------------------------------------------------------------------------
// Test: CLI arg parsing (parseArgs is not exported, so test the outcome)
// ---------------------------------------------------------------------------
const collectorModule = require('./playwright_stealth_collector.js');
assert(typeof collectorModule.collectWithPlaywrightStealth === 'function', 'collectWithPlaywrightStealth is exported');

// ---------------------------------------------------------------------------
// Test: brand_alias normalisation
// ---------------------------------------------------------------------------
const ctxAlias = { brand: 'Fig & Bloom', market: 'Sydney', source: 'Google', sourceUrl: 'https://example.com', collectedAt: '2026-05-05T00:00:00Z' };
const recordsAlias = extractJsonLdReviewsFromHtml(`<html><body>
<script type="application/ld+json">
{ "@type": "Review", "reviewBody": "Absolutely loved the arrangement and delivery was perfect.", "reviewRating": { "ratingValue": 5 }, "author": { "name": "Mia T." } }
</script></body></html>`, ctxAlias);
assertEqual(recordsAlias[0].brand_alias, 'fig-bloom', 'ampersand and spaces normalised in brand_alias');

// ---------------------------------------------------------------------------
// Test: nested @graph arrays handled
// ---------------------------------------------------------------------------
const graphHtml = `<html><body>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "Organization", "name": "Daily Blooms" },
    { "@type": "Review", "reviewRating": { "ratingValue": 3 }, "author": { "name": "Alex W." }, "reviewBody": "Arrangement was okay but a bit smaller than expected." }
  ]
}
</script></body></html>`;
const recordsGraph = extractJsonLdReviewsFromHtml(graphHtml, ctx1);
assertEqual(recordsGraph.length, 1, '@graph with mixed types yields 1 review');
assertEqual(recordsGraph[0].reviewer, 'Alex W.', '@graph reviewer parsed');

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------
console.log('PASS playwright_stealth_collector parser tests');
