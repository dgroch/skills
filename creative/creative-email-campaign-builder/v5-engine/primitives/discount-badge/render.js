/**
 * discount-badge
 *
 * "20% OFF" style badge overlay for product images in sale campaigns.
 * Used in: BFCM, LTV incentive, Sale-Promo (30% of Sale emails).
 * Pattern: Small badge overlaid on product image or placed above product card.
 *
 * Note: For email-safe overlay, this renders as a badge positioned above the product image.
 * True CSS overlay is not email-safe; this uses a table-based approach.
 *
 * @param {string} text - Badge text (e.g., "20% OFF")
 * @param {string} [bgColor="#000000"] - Badge background color
 * @param {string} [textColor="#FFFFFF"] - Badge text color
 * @param {string} [fontSize=11] - Font size
 * @param {string} [padding="6px 12px"] - Badge padding
 * @param {string} [letterSpacing=1] - Letter spacing
 * @param {string} [align="left"] - "left" | "right" | "center" alignment on product
 */
module.exports = function(opts) {
  const text = opts.text || '';
  const bgColor = opts.bgColor || '#000000';
  const textColor = opts.textColor || '#FFFFFF';
  const fontSize = opts.fontSize || 11;
  const padding = opts.padding || '6px 12px';
  const letterSpacing = opts.letterSpacing || 1;
  const align = opts.align || 'left';

  return `
<!-- DISCOUNT BADGE -->
<table role="presentation" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="${align}" style="background-color: ${bgColor};">
      <span style="display: inline-block; padding: ${padding}; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: ${fontSize}px; font-weight: 700; letter-spacing: ${letterSpacing}px; text-transform: uppercase; color: ${textColor};">
        ${text}
      </span>
    </td>
  </tr>
</table>
<!-- /DISCOUNT BADGE -->
`;
};
