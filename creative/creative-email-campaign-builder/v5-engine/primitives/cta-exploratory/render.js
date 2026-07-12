/**
 * cta-exploratory
 *
 * Exploratory CTA button for product launches and discovery campaigns.
 * Used in: Product Launch ("DISCOVER MAISON BLANCHE", "SEE WHAT'S NEW", "DISCOVER THE SCENT")
 * Pattern: Can be black or outline style, exploratory language.
 *
 * @param {string} text - Button text (e.g., "DISCOVER MAISON BLANCHE")
 * @param {string} url - Button URL
 * @param {string} [variant="primary"] - "primary" (solid) or "outline" (border only)
 * @param {string} [bgColor="#000000"] - Button background (primary) or border color (outline)
 * @param {string} [textColor="#FFFFFF"] - Text color (primary) or text color (outline)
 * @param {string} [fontSize=13] - Font size
 * @param {string} [letterSpacing=2] - Letter spacing
 * @param {string} [padding="14px 40px"] - Button padding
 * @param {string} [align="center"] - Alignment
 */
module.exports = function(opts) {
  const text = opts.text || '';
  const url = opts.url || '#';
  const variant = opts.variant || 'primary';
  const bgColor = opts.bgColor || '#000000';
  const textColor = opts.textColor || '#FFFFFF';
  const fontSize = opts.fontSize || 13;
  const letterSpacing = opts.letterSpacing || 2;
  const padding = opts.padding || '14px 40px';
  const align = opts.align || 'center';

  let style;
  if (variant === 'outline') {
    style = `background-color: transparent; border: 1.5px solid ${bgColor}; color: ${textColor};`;
  } else {
    style = `background-color: ${bgColor}; color: ${textColor};`;
  }

  return `
<!-- CTA EXPLORATORY -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="${align}" style="padding: 16px 0;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td align="center" style="${style}">
            <a href="${url}" target="_blank" style="display: inline-block; padding: ${padding}; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: ${fontSize}px; font-weight: 700; letter-spacing: ${letterSpacing}px; text-transform: uppercase; color: ${textColor}; text-decoration: none;">
              ${text}
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
<!-- /CTA EXPLORATORY -->
`;
};
