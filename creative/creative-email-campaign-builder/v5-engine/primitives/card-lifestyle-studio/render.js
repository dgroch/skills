/**
 * Primitive: card-lifestyle-studio
 *
 * Lifestyle+Studio stacked product card — one hero/spotlight product per email.
 * Section headline → lifestyle image 600×400 → studio image 600×500 → product info.
 * HandFlower illustration is locked (bottom-right of info section).
 *
 * @param {object} opts
 * @param {string} opts.sectionSuper - Section super-label e.g. "Mother's Day · Spotlight"
 * @param {string} opts.sectionHeadline - Lust headline (font-weight:normal locked)
 * @param {string} opts.lifestyleImage - Lifestyle/contextual photo URL (600×400px display)
 * @param {string} opts.studioImage - Studio/clean-bg product photo URL (600×500px display)
 * @param {string} opts.productLabel - Label e.g. "Bouquet · Seasonal · Same Day Available"
 * @param {string} opts.productName - Product name (Lust font, sentence case)
 * @param {string} opts.productOccasion - Occasion headline, italic
 * @param {string} opts.productDesc - 1–2 sentence description
 * @param {string} opts.productPrice - Price e.g. "From $89 · Same Day Available"
 * @param {string} opts.ctaText - CTA button text e.g. "Shop Garden Natives"
 * @param {string} opts.ctaUrl - CTA link URL
 * @param {string} opts.assetsBase - CDN base path for illustrations (default: Shopify CDN)
 * @param {string} opts.borderColor - Border color (default: "#e8e2da")
 * @param {object} opts.theme - Theme object (injected by compose)
 * @returns {string} HTML string for <tr> row
 */
module.exports = function renderCardLifestyleStudio(opts = {}) {
  const {
    sectionSuper,
    sectionHeadline,
    lifestyleImage,
    studioImage,
    productLabel,
    productName,
    productOccasion,
    productDesc,
    productPrice,
    ctaText,
    ctaUrl,
    assetsBase = 'https://cdn.shopify.com/s/files/1/0657/8723/2489/files',
    borderColor = '#e8e2da',
    theme = {}
  } = opts;

  if (!lifestyleImage || !studioImage) {
    throw new Error('[card-lifestyle-studio] lifestyleImage and studioImage are required');
  }

  return `<tr><td>
<!-- Section intro headline -->
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid ${borderColor};">
  <tr>
    <td class="sp" align="center" style="padding:40px 48px 24px;background:#ffffff;text-align:center;">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 14px 0;">${sectionSuper || ''}</p>
      <h2 class="sh" style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:26px;color:#000000;line-height:1.2;margin:0;">${sectionHeadline || ''}</h2>
    </td>
  </tr>
</table>
<!-- Lifestyle image — 600×400, object-position:center 25% shows subject -->
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td style="padding:0;overflow:hidden;">
      <img src="${lifestyleImage}" width="600" height="400" alt="" style="display:block;width:600px;height:400px;object-fit:cover;object-position:center 25%;">
    </td>
  </tr>
</table>
<!-- Studio image — 600×500, object-position:center top shows arrangement -->
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid ${borderColor};">
  <tr>
    <td style="padding:0;overflow:hidden;">
      <img src="${studioImage}" width="600" height="500" alt="" style="display:block;width:600px;height:500px;object-fit:cover;object-position:center top;">
    </td>
  </tr>
</table>
<!-- Product info -->
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid ${borderColor};">
  <tr>
    <td class="sp" align="center" style="padding:40px 64px;background:#ffffff;text-align:center;position:relative;overflow:hidden;">
      <!-- HandFlower illustration — bottom-right, 220px, locked -->
      <img src="${assetsBase}/HandRose_White.png" alt="" style="position:absolute;right:-20px;bottom:-20px;height:220px;width:auto;opacity:0.09;display:block;">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 10px 0;position:relative;z-index:1;">${productLabel || ''}</p>
      <h3 class="pn" style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:24px;color:#000000;line-height:1.15;margin:0 0 10px 0;position:relative;z-index:1;">${productName || ''}</h3>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#666666;line-height:1.7;margin:0 0 8px 0;font-style:italic;position:relative;z-index:1;">${productOccasion || ''}</p>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#444444;line-height:1.75;margin:0 0 22px 0;max-width:400px;margin-left:auto;margin-right:auto;position:relative;z-index:1;">${productDesc || ''}</p>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:14px;color:#000000;margin:0 0 26px 0;position:relative;z-index:1;">${productPrice || ''}</p>
      <a href="${ctaUrl || '#'}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#000000;color:#ffffff;text-decoration:none;padding:14px 40px;display:inline-block;position:relative;z-index:1;">${ctaText || 'SHOP NOW'}</a>
    </td>
  </tr>
</table>
</td></tr>`;
};
