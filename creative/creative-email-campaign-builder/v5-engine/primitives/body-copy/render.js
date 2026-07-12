/**
 * Primitive: body-copy
 *
 * Body copy with illustration accent (HandRose bottom-right).
 * White background, centered text with max-width constraint.
 *
 * @param {object} opts
 * @param {string} opts.superLabel - Small uppercase label above headline
 * @param {string} opts.headline - Main headline, Lust font, sentence case
 * @param {string} opts.bodyP1 - First paragraph text
 * @param {string} [opts.bodyP2] - Second paragraph text (optional)
 * @param {string} [opts.assetsBase] - Base URL for illustration assets (default: '{{ASSETS_BASE}}')
 * @param {string} [opts.illustration] - Illustration name (default: HandRose_White.png)
 * @returns {string} HTML string
 */
module.exports = function renderBodyCopy(opts = {}) {
  const {
    superLabel = '',
    headline,
    bodyP1,
    bodyP2 = '',
    assetsBase = '{{ASSETS_BASE}}',
    illustration = 'HandRose_White.png'
  } = opts;

  if (!headline) {
    throw new Error('[body-copy] headline is required');
  }

  if (!bodyP1) {
    throw new Error('[body-copy] bodyP1 is required');
  }

  const superLabelHtml = superLabel
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 14px 0;position:relative;z-index:1;">${superLabel}</p>`
    : '';

  const bodyP1Html = `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:14px;color:#444444;line-height:1.85;margin:0 auto 14px auto;max-width:440px;position:relative;z-index:1;">${bodyP1}</p>`;

  const bodyP2Html = bodyP2
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:14px;color:#444444;line-height:1.85;margin:0 auto;max-width:440px;position:relative;z-index:1;">${bodyP2}</p>`
    : '';

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e8e2da;">
  <tr>
    <td class="sp" align="center" style="padding:44px 64px;background:#ffffff;text-align:center;position:relative;overflow:hidden;">
      <!-- HandRose illustration — bottom-right, locked -->
      <img src="${assetsBase}/${illustration}" alt="" style="position:absolute;right:-20px;bottom:-20px;height:240px;width:auto;opacity:0.10;display:block;">
      ${superLabelHtml}
      <h2 class="sh" style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:28px;color:#000000;line-height:1.2;margin:0 0 20px 0;position:relative;z-index:1;">${headline}</h2>
      ${bodyP1Html}
      ${bodyP2Html}
    </td>
  </tr>
</table>
</td></tr>`;
};
