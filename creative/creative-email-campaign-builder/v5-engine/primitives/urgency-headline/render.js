/**
 * urgency-headline
 *
 * Bold, urgent headline for time-sensitive campaigns.
 * Used in: BFCM "Flash Sale Ends Tonight", LTV "Wilts in 2 Weeks", Holiday "Last Chance"
 * Pattern: Large, bold sans-serif, often with accent color or urgency language.
 *
 * @param {string} headline - Main urgency text (e.g., "Flash Sale Ends Tonight")
 * @param {string} [subheadline] - Optional supporting text (e.g., "20% OFF FLOWERS")
 * @param {string} [headlineColor="#000000"] - Headline color
 * @param {string} [subColor="#666666"] - Subheadline color
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [accentColor] - Optional accent bar color (e.g., "#CC0000" for urgency)
 * @param {string} [textAlign="center"] - Text alignment
 * @param {number} [headlineSize=32] - Headline font size
 * @param {number} [subSize=16] - Subheadline font size
 */
module.exports = function(opts) {
  const headline = opts.headline || '';
  const subheadline = opts.subheadline || '';
  const headlineColor = opts.headlineColor || '#000000';
  const subColor = opts.subColor || '#666666';
  const bgColor = opts.bgColor || '#FFFFFF';
  const accentColor = opts.accentColor || '';
  const textAlign = opts.textAlign || 'center';
  const hSize = opts.headlineSize || 32;
  const sSize = opts.subSize || 16;

  const accentBar = accentColor ? `
    <tr>
      <td style="height: 3px; background-color: ${accentColor};"></td>
    </tr>
  ` : '';

  return `
<!-- URGENCY HEADLINE -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  ${accentBar}
  <tr>
    <td align="center" style="padding: 32px 24px; background-color: ${bgColor};">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 552px;">
        <tr>
          <td align="${textAlign}" style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: ${hSize}px; font-weight: 700; line-height: 1.1; letter-spacing: -0.5px; color: ${headlineColor};">
            ${headline}
          </td>
        </tr>
        ${subheadline ? `
        <tr>
          <td align="${textAlign}" style="padding-top: 12px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: ${sSize}px; font-weight: 400; line-height: 1.4; color: ${subColor};">
            ${subheadline}
          </td>
        </tr>
        ` : ''}
      </table>
    </td>
  </tr>
  ${accentBar}
</table>
<!-- /URGENCY HEADLINE -->
`;
};
