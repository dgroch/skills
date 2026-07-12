/**
 * Primitive: body-copy-plain
 *
 * Body copy without illustration accent.
 * White background, centered text. HTML-safe, no positioned elements.
 *
 * @param {object} opts
 * @param {string} opts.superLabel - Small uppercase label above headline
 * @param {string} opts.headline - Main headline, Lust font, sentence case
 * @param {string} opts.bodyP1 - First paragraph text
 * @param {string} [opts.bodyP2] - Second paragraph text (optional)
 * @returns {string} HTML string
 */
module.exports = function renderBodyCopyPlain(opts = {}) {
  const {
    superLabel = '',
    headline,
    bodyP1,
    bodyP2 = ''
  } = opts;

  if (!headline) {
    throw new Error('[body-copy-plain] headline is required');
  }

  if (!bodyP1) {
    throw new Error('[body-copy-plain] bodyP1 is required');
  }

  const superLabelHtml = superLabel
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 14px 0;">${superLabel}</p>`
    : '';

  const bodyP2Html = bodyP2
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:14px;color:#444444;line-height:1.85;margin:0 auto;max-width:440px;">${bodyP2}</p>`
    : '';

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e8e2da;">
  <tr>
    <td class="sp" align="center" style="padding:44px 64px;background:#ffffff;text-align:center;">
      ${superLabelHtml}
      <h2 class="sh" style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:28px;color:#000000;line-height:1.2;margin:0 0 20px 0;">${headline}</h2>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:14px;color:#444444;line-height:1.85;margin:0 auto 14px auto;max-width:440px;">${bodyP1}</p>
      ${bodyP2Html}
    </td>
  </tr>
</table>
</td></tr>`;
};
