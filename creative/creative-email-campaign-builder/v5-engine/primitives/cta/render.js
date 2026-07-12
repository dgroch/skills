/**
 * Primitive: cta
 *
 * Call-to-action buttons: primary, secondary, stacked.
 *
 * @param {object} opts
 * @param {Array} opts.buttons - Array of { text, href, variant }
 * @param {string} opts.align - "left" | "center" | "right" (default: "center")
 * @param {string} opts.padding - Override padding
 * @param {object} opts.theme - Theme object
 * @returns {string} HTML string
 */
module.exports = function renderCta(opts = {}) {
  const {
    buttons = [],
    align = 'center',
    padding = '24px 48px',
    theme = {}
  } = opts;

  const palette = theme.palette || {};
  const components = theme.components || {};
  const ctaStyle = components.cta || {};
  const bodyFont = (theme.typography || {}).body?.family || '-apple-system, sans-serif';

  if (!Array.isArray(buttons) || buttons.length === 0) {
    throw new Error('[cta] buttons array is required and must not be empty');
  }

  function renderButton(btn, index) {
    const isPrimary = btn.variant === 'primary' || (!btn.variant && index === 0);

    const bg = isPrimary
      ? (ctaStyle.background || palette.accent || '#1A1A1A')
      : 'transparent';
    const textColor = isPrimary
      ? (ctaStyle.text || '#FFFFFF')
      : (palette.accent || '#1A1A1A');
    const border = isPrimary
      ? 'none'
      : `2px solid ${palette.accent || '#1A1A1A'}`;
    const borderRadius = ctaStyle.borderRadius || '0px';
    const btnPadding = ctaStyle.padding || '14px 32px';

    const spacer = index > 0 ? 'margin-left:16px;' : '';

    return `<a href="${btn.href}" target="_blank" style="display:inline-block;${spacer}background:${bg};color:${textColor};border:${border};border-radius:${borderRadius};padding:${btnPadding};font-family:${bodyFont};font-size:15px;font-weight:600;text-decoration:none;text-align:center;">${btn.text}</a>`;
  }

  const buttonsHtml = buttons.map((btn, i) => renderButton(btn, i)).join('\n        ');

  return `
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td align="${align}" style="padding:${padding};">
      ${buttonsHtml}
    </td>
  </tr>
</table>`;
};
