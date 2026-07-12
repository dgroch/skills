/**
 * Primitive: divider-line
 *
 * Simple 1px horizontal rule divider.
 * Static — no tokens or options needed.
 *
 * @param {object} [opts]
 * @param {string} [opts.color] - Line color (default: #e8e2da)
 * @returns {string} HTML string
 */
module.exports = function renderDividerLine(opts = {}) {
  const {
    color = '#e8e2da'
  } = opts;

  return `<tr><td style="padding:0;border-top:1px solid ${color};height:1px;line-height:1px;font-size:1px;">&nbsp;</td></tr>`;
};
