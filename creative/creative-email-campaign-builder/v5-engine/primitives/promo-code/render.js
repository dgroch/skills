/**
 * Primitive: promo-code
 *
 * Dashed border promo code block with Lust code text.
 * White background, centered layout.
 *
 * @param {object} opts
 * @param {string} opts.promoLabel - Label above code (e.g. "Your exclusive offer")
 * @param {string} opts.promoCode - The code itself (e.g. "MUMDAY25")
 * @param {string} opts.promoTerms - Terms text (e.g. "Orders over $130. Valid until May 5.")
 * @param {string} opts.ctaText - CTA button text (e.g. "Shop Now")
 * @param {string} opts.ctaUrl - CTA button URL
 * @returns {string} HTML string
 */
module.exports = function renderPromoCode(opts = {}) {
  const {
    promoLabel = '',
    promoCode,
    promoTerms = '',
    ctaText = 'Shop Now',
    ctaUrl
  } = opts;

  if (!promoCode) {
    throw new Error('[promo-code] promoCode is required');
  }

  if (!ctaUrl) {
    throw new Error('[promo-code] ctaUrl is required');
  }

  const promoLabelHtml = promoLabel
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#aaaaaa;margin:0 0 14px 0;">${promoLabel}</p>`
    : '';

  const promoTermsHtml = promoTerms
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:12px;color:#666666;margin:0 0 22px 0;">${promoTerms}</p>`
    : '';

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e8e2da;">
  <tr>
    <td class="sp" align="center" style="padding:40px 48px;background:#ffffff;text-align:center;">
      ${promoLabelHtml}
      <div style="display:inline-block;border:2px dashed #000000;padding:12px 32px;margin:0 0 12px 0;">
        <span style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:20px;color:#000000;letter-spacing:.08em;">${promoCode}</span>
      </div>
      ${promoTermsHtml}
      <a href="${ctaUrl}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#000000;color:#ffffff;text-decoration:none;padding:14px 40px;display:inline-block;">${ctaText}</a>
    </td>
  </tr>
</table>
</td></tr>`;
};
