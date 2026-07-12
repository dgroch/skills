/**
 * card-upsell
 *
 * Greeting card add-on section for holiday campaigns.
 * Used in: Mother's Day, Valentine's, Christmas (20% of Holiday emails).
 * Pattern: "Include a Heartfelt Message" with card image preview + CTA.
 *
 * @param {string} headline - Headline (e.g., "Include a Heartfelt Message")
 * @param {string} bodyText - Supporting text
 * @param {string} ctaText - CTA button text (e.g., "ADD A CARD")
 * @param {string} ctaUrl - CTA URL
 * @param {string} [bgColor="#EBE5DF"] - Background color (50% Clay default)
 * @param {string} [textColor="#333333"] - Text color
 * @param {string} [cardImageUrl] - Optional card preview image URL
 */
module.exports = function(opts) {
  const headline = opts.headline || 'Include a Heartfelt Message';
  const bodyText = opts.bodyText || '';
  const ctaText = opts.ctaText || 'ADD A CARD';
  const ctaUrl = opts.ctaUrl || '#';
  const bgColor = opts.bgColor || '#EBE5DF';
  const textColor = opts.textColor || '#333333';
  const cardImageUrl = opts.cardImageUrl || '';

  return `
<!-- CARD UPSELL -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 32px 24px; background-color: ${bgColor};">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 552px;">
        <tr>
          <td align="center" style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 20px; font-weight: 700; line-height: 1.3; color: ${textColor};">
            ${headline}
          </td>
        </tr>
        ${bodyText ? `
        <tr>
          <td align="center" style="padding-top: 12px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 300; line-height: 1.6; color: ${textColor};">
            ${bodyText}
          </td>
        </tr>
        ` : ''}
        ${cardImageUrl ? `
        <tr>
          <td align="center" style="padding-top: 24px;">
            <img src="${cardImageUrl}" alt="Greeting Card Preview" width="200" style="display: block; max-width: 200px; width: 100%; height: auto;" />
          </td>
        </tr>
        ` : ''}
        <tr>
          <td align="center" style="padding-top: 24px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="center" style="background-color: #000000;">
                  <a href="${ctaUrl}" target="_blank" style="display: inline-block; padding: 12px 32px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #ffffff; text-decoration: none;">
                    ${ctaText}
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
<!-- /CARD UPSELL -->
`;
};
