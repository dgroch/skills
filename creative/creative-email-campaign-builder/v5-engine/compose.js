/**
 * v5-engine: compose.js
 *
 * Main composition pipeline.
 * Takes a brief + layout + theme → produces full HTML email.
 *
 * Fig & Bloom design system. Single theme: fig-and-bloom.
 * Includes @font-face for Lust, Cervanttis, NeuzeitGro, Gill Sans.
 * Mobile responsive CSS for all product card primitives.
 */

const path = require('path');
const fs = require('fs');

const LAYOUTS_DIR = path.join(__dirname, 'layouts');
const PRIMITIVES_DIR = path.join(__dirname, 'primitives');
const THEMES_PATH = path.join(__dirname, 'themes.json');

const DEFAULT_ASSETS_BASE = 'https://cdn.shopify.com/s/files/1/0657/8723/2489/files';

/**
 * Load a theme by name
 */
function loadTheme(themeName) {
  const themes = JSON.parse(fs.readFileSync(THEMES_PATH, 'utf8'));
  // Default to fig-and-bloom if not specified
  const name = themeName || 'fig-and-bloom';
  const theme = themes[name];
  if (!theme) {
    throw new Error(`[compose] Theme not found: ${name}. Available: ${Object.keys(themes).join(', ')}`);
  }
  return theme;
}

/**
 * Load a layout spec by name
 */
function loadLayout(layoutName) {
  const layoutPath = path.join(LAYOUTS_DIR, layoutName, 'layout.js');
  if (!fs.existsSync(layoutPath)) {
    throw new Error(`[compose] Layout not found: ${layoutName}`);
  }
  return require(layoutPath).getLayoutSpec();
}

/**
 * Load a primitive renderer by name
 */
function loadPrimitive(primitiveName) {
  const renderPath = path.join(PRIMITIVES_DIR, primitiveName, 'render.js');
  if (!fs.existsSync(renderPath)) {
    throw new Error(`[compose] Primitive not found: ${primitiveName}`);
  }
  return require(renderPath);
}

/**
 * Compose an email from brief data
 *
 * @param {object} brief - Brief JSON object
 * @param {object} opts - Override options
 * @param {string} opts.themeName - Override theme (default: 'fig-and-bloom')
 * @param {string} opts.layoutName - Override layout (default: brief.layout)
 * @param {object} opts.slotOverrides - Per-slot option overrides
 * @param {string} opts.assetsBase - CDN base for illustrations (default: Shopify CDN)
 * @returns {{ html: string, meta: object }}
 */
function compose(brief, opts = {}) {
  const themeName = opts.themeName || brief.theme || 'fig-and-bloom';
  const assetsBase = opts.assetsBase || DEFAULT_ASSETS_BASE;

  // Load theme
  const theme = loadTheme(themeName);

  const sections = [];

  // MODE 1: Slot-based brief (brief.slots defines order + primitive + options)
  if (brief.slots) {
    for (const [slotKey, slotDef] of Object.entries(brief.slots)) {
      const primitiveName = slotDef.primitive || slotKey;
      const renderer = loadPrimitive(primitiveName);

      // Build slot data from slot definition (everything except 'primitive')
      const slotData = { ...slotDef };
      delete slotData.primitive;

      // Inject theme and assetsBase
      slotData.theme = theme;
      slotData.assetsBase = slotData.assetsBase || assetsBase;

      try {
        const html = renderer(slotData);
        sections.push({ slot: slotKey, primitive: primitiveName, html });
      } catch (err) {
        sections.push({ slot: slotKey, primitive: primitiveName, html: null, error: err.message });
      }
    }
  }
  // MODE 2: Layout-based brief (uses layout spec for slot order)
  else {
    const layoutName = opts.layoutName || brief.layout;
    const slotOverrides = opts.slotOverrides || {};
    const layoutSpec = loadLayout(layoutName);
    const slotConfig = layoutSpec.slotConfig;

    for (const [slotKey, config] of Object.entries(slotConfig)) {
      const primitiveName = config.primitive || slotKey.replace(/-\d+$/, '');
      const renderer = loadPrimitive(primitiveName);

      let slotData = { ...config.defaults };
      slotData = mapBriefToSlot(brief, slotKey, primitiveName, slotData);

      if (slotOverrides[slotKey]) {
        slotData = { ...slotData, ...slotOverrides[slotKey] };
      }

      slotData.theme = theme;
      slotData.assetsBase = slotData.assetsBase || assetsBase;

      try {
        const html = renderer(slotData);
        sections.push({ slot: slotKey, primitive: primitiveName, html });
      } catch (err) {
        if (config.required) {
          throw new Error(`[compose] Required slot "${slotKey}" failed: ${err.message}`);
        }
        sections.push({ slot: slotKey, primitive: primitiveName, html: null, error: err.message });
      }
    }
  }

  // Assemble into email wrapper
  const palette = theme.palette || {};
  const bgColor = palette.bodyBg || '#2c2825';
  const maxWidth = 600;

  const innerHtml = sections
    .filter(s => s.html)
    .map(s => s.html)
    .join('\n');

  const fullHtml = wrapEmail(innerHtml, { bgColor, maxWidth, subject: brief.subject, assetsBase });

  return {
    html: fullHtml,
    meta: {
      theme: themeName,
      layout: brief.layout || 'slot-based',
      slots: sections.map(s => ({
        slot: s.slot,
        primitive: s.primitive,
        rendered: !!s.html,
        error: s.error || null
      })),
      subject: brief.subject,
      preview: brief.preview
    }
  };
}

/**
 * Map brief fields to slot data based on slot key and primitive name.
 * Supports all Fig & Bloom product card primitives.
 */
function mapBriefToSlot(brief, slotKey, primitiveName, defaults) {
  const data = { ...defaults };

  // Match by primitive name first, then fall back to slotKey
  switch (primitiveName) {
    case 'header':
      data.logoSrc = brief.logoSrc || data.logoSrc;
      break;

    case 'hero':
      data.imageSrc = brief.heroImage || data.imageSrc;
      data.headline = brief.headline || data.headline;
      data.subheadline = brief.subheadline || data.subheadline;
      break;

    case 'body':
      if (brief.bodyContent) {
        data.content = brief.bodyContent;
      }
      break;

    case 'card-horizontal':
    case 'card-horizontal-reversed':
      // Map from brief.products array by index or explicit slot mapping
      if (brief.products && brief.products.length > 0) {
        // Try to extract product index from slotKey (e.g. "product-1" -> index 0)
        const indexMatch = slotKey.match(/(\d+)$/);
        const idx = indexMatch ? parseInt(indexMatch[1], 10) - 1 : 0;
        const product = brief.products[idx] || brief.products[0];
        if (product) {
          data.productImage = product.image || product.productImage || data.productImage;
          data.productName = product.name || product.productName || data.productName;
          data.productLabel = product.label || product.productLabel || data.productLabel;
          data.productOccasion = product.occasion || product.productOccasion || data.productOccasion;
          data.productPrice = product.price || product.productPrice || data.productPrice;
          data.productUrl = product.url || product.productUrl || data.productUrl;
        }
      }
      break;

    case 'card-lifestyle-studio':
      if (brief.spotlightProduct || brief.products) {
        const sp = brief.spotlightProduct || brief.products[0] || {};
        data.sectionSuper = sp.sectionSuper || brief.sectionSuper || data.sectionSuper;
        data.sectionHeadline = sp.sectionHeadline || brief.sectionHeadline || data.sectionHeadline;
        data.lifestyleImage = sp.lifestyleImage || data.lifestyleImage;
        data.studioImage = sp.studioImage || data.studioImage;
        data.productLabel = sp.label || sp.productLabel || data.productLabel;
        data.productName = sp.name || sp.productName || data.productName;
        data.productOccasion = sp.occasion || sp.productOccasion || data.productOccasion;
        data.productDesc = sp.description || sp.productDesc || data.productDesc;
        data.productPrice = sp.price || sp.productPrice || data.productPrice;
        data.ctaText = sp.ctaText || data.ctaText;
        data.ctaUrl = sp.ctaUrl || sp.url || data.ctaUrl;
      }
      break;

    case 'card-single-testimonial':
      if (brief.products && brief.products.length > 0) {
        const indexMatch = slotKey.match(/(\d+)$/);
        const idx = indexMatch ? parseInt(indexMatch[1], 10) - 1 : 0;
        const product = brief.products[idx] || brief.products[0];
        if (product) {
          data.productImage = product.image || product.productImage || data.productImage;
          data.productName = product.name || product.productName || data.productName;
          data.productLabel = product.label || product.productLabel || data.productLabel;
          data.productOccasion = product.occasion || product.productOccasion || data.productOccasion;
          data.productPrice = product.price || product.productPrice || data.productPrice;
          data.productUrl = product.url || product.productUrl || data.productUrl;
          data.quote = product.quote || product.reviewText || data.quote;
          data.attribution = product.attribution || product.reviewerName || data.attribution;
          data.rating = product.rating || data.rating;
        }
      }
      break;

    case 'cta':
      data.buttons = [];
      if (brief.primaryCta) {
        data.buttons.push({ ...brief.primaryCta, variant: 'primary' });
      }
      if (brief.secondaryCta) {
        data.buttons.push({ ...brief.secondaryCta, variant: 'secondary' });
      }
      break;

    case 'footer':
      data.links = brief.footerLinks || [];
      data.unsubscribeHref = brief.unsubscribeHref;
      data.companyName = brief.companyName || 'Fig & Bloom';
      data.companyAddress = brief.companyAddress || '';
      break;

    default:
      // Legacy slot key matching (body-main, body-closing, etc.)
      if (slotKey === 'body-main' || slotKey === 'body') {
        if (brief.bodyContent) { data.content = brief.bodyContent; }
      } else if (slotKey === 'body-closing') {
        if (brief.closingContent) { data.content = brief.closingContent; }
      } else if (slotKey === 'product') {
        if (brief.products) {
          data.products = brief.products;
          data.heading = brief.productHeading;
        }
      }
      break;
  }

  return data;
}

/**
 * Wrap inner HTML in email boilerplate with @font-face and mobile CSS.
 *
 * Includes:
 * - @font-face declarations for Lust, Cervanttis, NeuzeitGro, Gill Sans
 * - Full mobile responsive CSS for all Fig & Bloom product card primitives
 * - Body background color (default: #2c2825)
 * - MSO conditional comments for Office compatibility
 *
 * @param {string} innerHtml - Rendered component HTML
 * @param {object} opts
 * @param {string} opts.bgColor - Body background (default: "#2c2825")
 * @param {number} opts.maxWidth - Email width in px (default: 600)
 * @param {string} opts.subject - Email subject line for <title>
 * @param {string} opts.assetsBase - CDN base for font files (default: Shopify CDN)
 * @returns {string} Full HTML document
 */
function wrapEmail(innerHtml, opts = {}) {
  const {
    bgColor = '#2c2825',
    maxWidth = 600,
    subject = '',
    assetsBase = DEFAULT_ASSETS_BASE
  } = opts;

  return `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>${subject}</title>
<!--[if !mso]><!-->
<style>
@font-face{font-family:'Cervanttis';src:url('${assetsBase}/cervanttis.ttf') format('truetype');font-weight:400;font-style:normal;font-display:swap;}
@font-face{font-family:'Lust';src:url('${assetsBase}/Lust-Regular.woff2') format('woff2');font-weight:normal;font-style:normal;font-display:swap;}
@font-face{font-family:'NeuzeitGro';src:url('${assetsBase}/NeuzeitGro-Lig.otf') format('opentype');font-weight:300;font-style:normal;font-display:swap;}
@font-face{font-family:'NeuzeitGro';src:url('${assetsBase}/NeuzeitGro-Bol.otf') format('opentype');font-weight:700;font-style:normal;font-display:swap;}
@font-face{font-family:'Gill Sans';src:url('${assetsBase}/Gill%20Sans%20Light.otf') format('opentype');font-weight:300;font-style:normal;font-display:swap;}
@font-face{font-family:'Gill Sans';src:url('${assetsBase}/Gill%20Sans.otf') format('opentype');font-weight:400;font-style:normal;font-display:swap;}
@font-face{font-family:'Gill Sans';src:url('${assetsBase}/Gill%20Sans%20Bold.otf') format('opentype');font-weight:700;font-style:normal;font-display:swap;}
</style>
<!--<![endif]-->
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body,table,td{font-family:'Gill Sans','Gill Sans MT',Calibri,sans-serif;}
img{border:0;line-height:100%;outline:none;text-decoration:none;display:block;}
table{border-collapse:collapse;}

@media only screen and (max-width:600px){
  .ew{width:100%!important;}
  .hh{font-size:38px!important;line-height:1.0!important;}
  .sh{font-size:22px!important;}
  .pn{font-size:18px!important;}
  .uh{font-size:28px!important;}
  .sp{padding-left:24px!important;padding-right:24px!important;}
  .hp{padding:32px 24px!important;}
  .hc{display:block!important;width:100%!important;}
  .hi{display:block!important;width:100%!important;height:240px!important;}
  .hinfo{display:block!important;width:100%!important;padding:24px!important;}
  .pt{display:block!important;width:100%!important;}
  .ptimg{display:block!important;width:100%!important;border-right:none!important;border-bottom:1px solid #e8e2da!important;}
  .pttesti{display:block!important;width:100%!important;padding:32px 24px!important;}
  .ud{min-height:0!important;padding:56px 28px!important;}
  .uil{height:200px!important;}
  .cc{display:block!important;width:100%!important;border-right:none!important;border-bottom:1px solid #e8e2da;padding:16px 0!important;}
  .cc:last-child{border-bottom:none!important;}
  .fi{display:block!important;}
}
</style>
</head>
<body style="margin:0;padding:0;background:${bgColor};">
<center>
<table class="ew" width="${maxWidth}" cellpadding="0" cellspacing="0" border="0" style="width:${maxWidth}px;max-width:${maxWidth}px;background:#ffffff;margin:0 auto;">
${innerHtml}
</table>
</center>
</body></html>`;
}

module.exports = { compose, loadTheme, loadLayout, loadPrimitive, wrapEmail };
