/**
 * Primitive: divider-whitespace
 *
 * 48px whitespace breathing room divider.
 * Most editorial divider. Use between two text-heavy sections.
 *
 * @param {object} [opts]
 * @param {string} [opts.height] - Whitespace height in px (default: 48px)
 * @param {string} [opts.background] - Background color (default: #ffffff)
 * @returns {string} HTML string
 */
module.exports = function renderDividerWhitespace(opts = {}) {
  const {
    height = '48px',
    background = '#ffffff'
  } = opts;

  return `<tr><td style="padding:0;height:${height};background:${background};line-height:${height};font-size:${height};">&nbsp;</td></tr>`;
};
