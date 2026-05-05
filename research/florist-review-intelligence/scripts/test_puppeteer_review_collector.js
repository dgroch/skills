#!/usr/bin/env node
const assert = require('node:assert/strict');
const { extractJsonLdReviewsFromHtml, stableId } = require('./puppeteer_review_collector.js');

const html = `<!doctype html>
<html><head>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Review",
  "author": {"name": "A Reviewer"},
  "reviewRating": {"ratingValue": "5"},
  "datePublished": "2026-05-01",
  "name": "Beautiful flowers",
  "reviewBody": "The bouquet looked exactly like the photo and arrived on time."
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Review",
      "author": "Second Reviewer",
      "reviewRating": {"ratingValue": 2},
      "reviewBody": "Late delivery and the flowers were not fresh."
    }
  ]
}
</script>
</head><body></body></html>`;

const records = extractJsonLdReviewsFromHtml(html, {
  brand: 'Daily Blooms',
  market: 'Melbourne',
  source: 'Fixture',
  sourceUrl: 'https://example.test/reviews',
});

assert.equal(records.length, 2, 'extracts JSON-LD Review objects including @graph reviews');
assert.equal(records[0].brand, 'Daily Blooms');
assert.equal(records[0].market, 'Melbourne');
assert.equal(records[0].reviewer, 'A Reviewer');
assert.equal(records[0].rating, 5);
assert.equal(records[0].review_date, '2026-05-01');
assert.match(records[0].text, /looked exactly like the photo/);
assert.equal(records[1].reviewer, 'Second Reviewer');
assert.equal(records[1].rating, 2);
assert.match(records[1].text, /Late delivery/);
assert.equal(stableId('abc').length, 16);
console.log('PASS puppeteer_review_collector parser tests');
