/**
 * Primitive: card-single-testimonial
 *
 * Product column (340px, image 4:5) + testimonial column (260px, 50% Clay bg).
 * Face2 illustration is locked (bottom-right of testimonial col, 30% height).
 * No quote mark — stars sit above quote text.
 *
 * @param {object} opts
 * @param {string} opts.productImage - URL to 4:5 product photo (340×425 display, 680×850 source min)
 * @param {string} opts.productName - Product name (Lust font, sentence case)
 * @param {string} opts.productLabel - Label text
 * @param {string} opts.productOccasion - Occasion headline, italic
 * @param {string} opts.productPrice - Price text e.g. "From $89"
 * @param {string} opts.productUrl - Product page URL
 * @param {string} opts.quote - Review/quote text, no quote marks needed
 * @param {string} opts.attribution - Reviewer name e.g. "Sarah M., Sydney"
 * @param {number} opts.rating - Number of stars (1-5, default: 5)
 * @param {string} opts.assetsBase - CDN base path for illustrations (default: Shopify CDN)
 * @param {string} opts.starColor - Star color (default: "#C8A888")
 * @param {string} opts.testimonialBg - Testimonial column background (default: "#EBE5DF" = 50% Clay)
 * @param {string} opts.borderColor - Border color (default: "#e8e2da")
 * @param {object} opts.theme - Theme object (injected by compose)
 * @returns {string} HTML string for <tr> row
 */
module.exports = function renderCardSingleTestimonial(opts = {}) {
  const {
    productImage,
    productName,
    productLabel,
    productOccasion,
    productPrice,
    productUrl,
    quote,
    attribution,
    rating = 5,
    assetsBase = 'https://cdn.shopify.com/s/files/1/0657/8723/2489/files',
    starColor = '#C8A888',
    testimonialBg = '#EBE5DF',
    borderColor = '#e8e2da',
    theme = {}
  } = opts;

  if (!productImage) {
    throw new Error('[card-single-testimonial] productImage is required');
  }

  const stars = '★'.repeat(rating) + '☆'.repeat(5 - rating);

  return `<tr><td style="border-top:1px solid ${borderColor};">
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <!-- Product column — 340px -->
    <td class="ptimg" width="340" valign="top" style="width:340px;border-right:1px solid ${borderColor};vertical-align:top;">
      <img src="${productImage}" width="340" height="425" alt="${productName || ''}"
           style="display:block;width:340px;height:425px;object-fit:cover;object-position:center top;">
      <table width="340" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="padding:28px;">
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 8px 0;">${productLabel || ''}</p>
            <h3 class="pn" style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:22px;color:#000000;line-height:1.15;margin:0 0 8px 0;">${productName || ''}</h3>
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:12px;color:#666666;line-height:1.6;margin:0 0 14px 0;font-style:italic;">${productOccasion || ''}</p>
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:13px;color:#000000;margin:0 0 20px 0;">${productPrice || ''}</p>
            <a href="${productUrl || '#'}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.16em;text-transform:uppercase;background:#000000;color:#ffffff;text-decoration:none;padding:10px 24px;display:inline-block;">SHOP NOW</a>
          </td>
        </tr>
      </table>
    </td>
    <!-- Testimonial column — 260px, 50% Clay bg -->
    <td class="pttesti" valign="middle" style="background:${testimonialBg};padding:36px 28px;text-align:center;vertical-align:middle;position:relative;overflow:hidden;">
      <!-- Face2 illustration — bottom-right, 30% height, locked -->
      <img src="${assetsBase}/Face2_Black.png" alt="" style="position:absolute;right:-30px;bottom:-30px;height:calc(30% + 30px);width:auto;opacity:0.12;display:block;">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:14px;color:${starColor};letter-spacing:.08em;margin:0 0 18px 0;position:relative;z-index:1;">${stars}</p>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#333333;font-style:italic;line-height:1.8;margin:0 0 16px 0;position:relative;z-index:1;">${quote || ''}</p>
      <cite style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.08em;color:#999999;font-style:normal;display:block;position:relative;z-index:1;">— ${attribution || ''}</cite>
    </td>
  </tr>
</table>
</td></tr>`;
};
