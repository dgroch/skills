/**
 * Primitive: upsell-noir
 *
 * Dark closing beat section with Noir (#000) background.
 * Flanking HandRose illustrations (white, 25-28% opacity).
 * Cervanttis headline (must be lowercase).
 * Use max once per email, typically near the bottom.
 *
 * @param {object} opts
 * @param {string} opts.superLabel - Uppercase label (e.g. "Add to your gift")
 * @param {string} opts.headline - Cervanttis font, MUST be lowercase
 * @param {string} opts.body - Supporting copy, max ~30 words
 * @param {string} opts.ctaText - CTA button text
 * @param {string} opts.ctaUrl - CTA button URL
 * @param {string} [opts.assetsBase] - Base URL for illustration assets
 * @param {string} [opts.leftIllustration] - Left illustration (default: HandRose_White.png)
 * @param {string} [opts.rightIllustration] - Right illustration (default: HandRose_White.png)
 * @returns {string} HTML string
 */
module.exports = function renderUpsellNoir(opts = {}) {
  const {
    superLabel = '',
    headline,
    body,
    ctaText,
    ctaUrl,
    assetsBase = '{{ASSETS_BASE}}',
    leftIllustration = 'HandRose_White.png',
    rightIllustration = 'HandRose_White.png'
  } = opts;

  if (!headline) {
    throw new Error('[upsell-noir] headline is required');
  }

  if (!ctaText || !ctaUrl) {
    throw new Error('[upsell-noir] ctaText and ctaUrl are required');
  }

  const superLabelHtml = superLabel
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,0.40);margin:0 0 22px 0;position:relative;z-index:1;">${superLabel}</p>`
    : '';

  const bodyHtml = body
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:rgba(255,255,255,0.70);max-width:300px;margin:0 auto 28px auto;line-height:1.75;position:relative;z-index:1;">${body}</p>`
    : '';

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="#000000">
  <tr>
    <td class="ud" align="center" valign="middle" bgcolor="#000000"
        style="background:#000000;min-height:440px;padding:64px;text-align:center;position:relative;overflow:hidden;vertical-align:middle;">
      <!-- ${leftIllustration} left — bottom-anchored, 360px total, locked -->
      <img src="${assetsBase}/${leftIllustration}" class="uil" alt="" style="position:absolute;left:-16px;bottom:-60px;height:360px;width:auto;opacity:0.28;display:block;">
      <!-- ${rightIllustration} right — mirrored, locked -->
      <img src="${assetsBase}/${rightIllustration}" class="uil" alt="" style="position:absolute;right:-16px;bottom:-60px;height:360px;width:auto;opacity:0.22;display:block;transform:scaleX(-1);">
      ${superLabelHtml}
      <h2 class="uh" style="font-family:'Cervanttis','Palatino Linotype',Palatino,Georgia,serif;font-weight:400;font-style:normal;font-synthesis:none;-webkit-font-smoothing:antialiased;font-size:36px;color:#ffffff;line-height:1.0;margin:0 0 18px 0;position:relative;z-index:1;">${headline}</h2>
      <div style="width:36px;height:1px;background:rgba(255,255,255,0.22);margin:0 auto 22px auto;position:relative;z-index:1;"></div>
      ${bodyHtml}
      <a href="${ctaUrl}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#ffffff;color:#000000;text-decoration:none;padding:14px 40px;display:inline-block;position:relative;z-index:1;">${ctaText}</a>
    </td>
  </tr>
</table>
</td></tr>`;
};
