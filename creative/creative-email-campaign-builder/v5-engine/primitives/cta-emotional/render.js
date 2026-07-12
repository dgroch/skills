/**
 * cta-emotional
 *
 * Emotionally-framed CTA button for flow emails (abandonment, post-purchase, winback).
 * Used in: Abandonment ("BRING IT TO LIFE", "FINISH THE THOUGHT"),
 *           Post-purchase ("JOIN THE GROUP", "SHARE YOUR THOUGHTS")
 * Pattern: Black button, white text, all caps, but with emotional language.
 *
 * @param {string} text - Button text (e.g., "BRING IT TO LIFE")
 * @param {string} url - Button URL
 * @param {string} [bgColor="#000000"] - Button background color
 * @param {string} [textColor="#FFFFFF"] - Button text color
 * @param {string} [fontSize=13] - Font size
 * @param {string} [letterSpacing=2] - Letter spacing
 * @param {string} [padding="14px 40px"] - Button padding
 * @param {string} [align="center"] - Alignment
 */
module.exports = function(opts) {
  const text = opts.text || '';
  const url = opts.url || '#';
  const bgColor = opts.bgColor || '#000000';
  const textColor = opts.textColor || '#FFFFFF';
  const fontSize = opts.fontSize || 13;
  const letterSpacing = opts.letterSpacing || 2;
  const padding = opts.padding || '14px 40px';
  const align = opts.align || 'center';

  return `
<!-- CTA EMOTIONAL -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="${align}" style="padding: 16px 0;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td align="center" style="background-color: ${bgColor};">
            <a href="${url}" target="_blank" style="display: inline-block; padding: ${padding}; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: ${fontSize}px; font-weight: 700; letter-spacing: ${letterSpacing}px; text-transform: uppercase; color: ${textColor}; text-decoration: none;">
              ${text}
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
<!-- /CTA EMOTIONAL -->
`;
};
