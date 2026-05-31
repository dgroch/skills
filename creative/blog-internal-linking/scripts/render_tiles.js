#!/usr/bin/env node
/*
 * render_tiles.js — Fig & Bloom shoppable product tiles (email-style banner).
 *
 * Renders one PNG per product: a 4:5 product photo above a cream caption block
 * (occasion label, serif name, price). Tiles are composed images; the blog
 * embeds each as its own <a><img>, so they stay clickable and wrap on mobile.
 *
 * Usage:
 *   node render_tiles.js products.json ./out
 *
 * products.json = array of:
 *   { "id": "card-champagne",        // becomes out_<id>.png; keep it slug-safe
 *     "name": "Champagne",
 *     "label": "For birthdays",      // small-caps gold eyebrow
 *     "price": "$9.95",              // free text: "$9.95" or "From $127"
 *     "img": "https://.../photo.jpg",// the REAL product photo (honest)
 *     "kind": "card",                // "card" → "Greeting card · {price}"; else price as-is
 *     "desc": "Soft, sculptural."    // optional one-liner (products only)
 *   }
 *
 * Requires puppeteer (npm i puppeteer). Photos are fetched at render time, so
 * the machine needs outbound network to cdn.shopify.com (and fonts.googleapis.com).
 */
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const TOKENS = {
  bg: '#FAF6F0', ink: '#26221E', gold: '#B08D57', muted: '#6E655C',
  serif: "'Cormorant Garamond', serif", sans: "'Jost', sans-serif",
  // Photo box is locked to 4:5 (matches the 1000x1250 product library).
  width: 600, ratio: 1.25,
};

const [,, productsPath, outDirArg] = process.argv;
if (!productsPath) { console.error('usage: node render_tiles.js products.json [outDir]'); process.exit(1); }
const outDir = outDirArg || './out';
fs.mkdirSync(outDir, { recursive: true });
const products = JSON.parse(fs.readFileSync(productsPath, 'utf8'));

const priceLine = (p) => p.kind === 'card' ? `Greeting card · ${p.price}` : p.price;
const tile = (p) => `
  <div class="tile" id="${p.id}">
    <div class="photo"><img src="${p.img}" crossorigin="anonymous"></div>
    <div class="meta">
      <div class="label">${p.label || ''}</div>
      <div class="name">${p.name}</div>
      ${p.desc ? `<div class="desc">${p.desc}</div>` : ''}
      <div class="price">${priceLine(p)}</div>
    </div>
  </div>`;

const html = `<!doctype html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Jost:wght@400;500&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{background:#fff;padding:40px;display:flex;flex-wrap:wrap;gap:40px;align-items:flex-start}
.tile{width:${TOKENS.width}px;background:${TOKENS.bg};overflow:hidden}
.photo{width:${TOKENS.width}px;height:${Math.round(TOKENS.width*TOKENS.ratio)}px;background:#fff;overflow:hidden}
.photo img{width:100%;height:100%;object-fit:cover;object-position:center;display:block}
.meta{padding:34px 38px 40px}
.label{font-family:${TOKENS.sans};font-weight:500;font-size:14px;letter-spacing:3px;text-transform:uppercase;color:${TOKENS.gold}}
.name{font-family:${TOKENS.serif};font-weight:600;font-size:46px;line-height:1.05;color:${TOKENS.ink};margin:10px 0 0}
.desc{font-family:${TOKENS.sans};font-weight:400;font-size:19px;color:${TOKENS.muted};margin-top:10px}
.price{font-family:${TOKENS.sans};font-weight:400;font-size:18px;letter-spacing:.5px;color:${TOKENS.ink};margin-top:16px}
</style></head><body>${products.map(tile).join('')}</body></html>`;

const htmlPath = path.join(outDir, '_tiles.html');
fs.writeFileSync(htmlPath, html);

(async () => {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 2000, deviceScaleFactor: 2 }); // 2x → ~1200px wide, crisp
  await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'networkidle0', timeout: 60000 });
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 800)); // let webfonts paint
  for (const p of products) {
    const el = await page.$('#' + p.id);
    if (!el) { console.error('missing tile', p.id); continue; }
    await el.screenshot({ path: path.join(outDir, `out_${p.id}.png`) });
    console.log('rendered', p.id);
  }
  await browser.close();
})();
