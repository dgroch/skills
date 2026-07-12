/**
 * Primitive: spacer
 *
 * Vertical whitespace.
 *
 * @param {object} opts
 * @param {number} opts.height - Height in px (default: 24)
 * @param {string} opts.background - Background color (default: transparent)
 * @param {object} opts.theme - Theme object
 * @returns {string} HTML string
 */
module.exports = function renderSpacer(opts = {}) {
  const {
    height = 24,
    background = 'transparent',
    theme = {}
  } = opts;

  if (typeof height !== 'number' || height < 0) {
    throw new Error('[spacer] height must be a non-negative number');
  }

  return `
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="height:${height}px;background:${background};font-size:1px;line-height:1px;">&nbsp;</td>
  </tr>
</table>`;
};
