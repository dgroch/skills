/**
 * Primitive: section-headline
 *
 * Section headline with optional super label (Lust font, 28px).
 * White background, centered, border-top separator.
 *
 * @param {object} opts
 * @param {string} opts.superLabel - Small uppercase label above headline (e.g. "Our Story")
 * @param {string} opts.headline - Main headline text, Lust font, sentence case
 * @param {string} [opts.background] - Background color (default: #ffffff)
 * @returns {string} HTML string
 */
module.exports = function renderSectionHeadline(opts = {}) {
  const {
    superLabel = '',
    headline,
    background = '#ffffff'
  } = opts;

  if (!headline) {
    throw new Error('[section-headline] headline is required');
  }

  const superLabelHtml = superLabel
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 14px 0;">${superLabel}</p>`
    : '';

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e8e2da;">
  <tr>
    <td class="sp" align="center" style="padding:40px 48px 28px;background:${background};text-align:center;">
      ${superLabelHtml}
      <h2 class="sh" style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:28px;color:#000000;line-height:1.2;margin:0;">${headline}</h2>
    </td>
  </tr>
</table>
</td></tr>`;
};
