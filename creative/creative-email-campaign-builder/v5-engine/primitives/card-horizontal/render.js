/**
 * Primitive: card-horizontal
 *
 * Horizontal product card — IMAGE LEFT / INFO RIGHT.
 * Image 280×350px (4:5), info panel 320px.
 * Alternate with card-horizontal-reversed for visual rhythm.
 *
 * @param {object} opts
 * @param {string} opts.productImage - URL to 4:5 product photo (280×350 display, 560×700 source min)
 * @param {string} opts.productName - Product name (Lust font, sentence case, font-weight:normal LOCKED)
 * @param {string} opts.productLabel - Label text e.g. "Vase Arrangement · Signature"
 * @param {string} opts.productOccasion - Occasion headline, italic
 * @param {string} opts.productPrice - Price text e.g. "From $139"
 * @param {string} opts.productUrl - Product page URL
 * @param {string} opts.borderColor - Border color (default: "#e8e2da")
 * @param {object} opts.theme - Theme object (injected by compose)
 * @returns {string} HTML string for <tr> row
 */
module.exports = function renderCardHorizontal(opts = {}) {
  const {
    productImage,
    productName,
    productLabel,
    productOccasion,
    productPrice,
    productUrl,
    borderColor = '#e8e2da',
    theme = {}
  } = opts;

  if (!productImage) {
    throw new Error('[card-horizontal] productImage is required');
  }

  return `<tr><td style="border-top:1px solid ${borderColor};">
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td class="hi" width="280" valign="top" style="width:280px;height:350px;padding:0;overflow:hidden;vertical-align:top;">
      <img src="${productImage}" width="280" height="350" alt="${productName || ''}"
           style="display:block;width:280px;height:350px;object-fit:cover;object-position:center top;">
    </td><td class="hinfo" valign="middle" style="padding:32px 28px 32px 32px;vertical-align:middle;">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 8px 0;">${productLabel || ''}</p>
      <h3 class="pn" style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:22px;color:#000000;line-height:1.15;margin:0 0 8px 0;">${productName || ''}</h3>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:12px;color:#666666;line-height:1.6;margin:0 0 14px 0;font-style:italic;">${productOccasion || ''}</p>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:13px;color:#000000;margin:0 0 22px 0;">${productPrice || ''}</p>
      <a href="${productUrl || '#'}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.16em;text-transform:uppercase;background:#000000;color:#ffffff;text-decoration:none;padding:10px 24px;display:inline-block;">SHOP NOW</a>
    </td>
  </tr>
</table>
</td></tr>`;
};
