/**
 * sentiment-product-row
 *
 * Horizontal product card with emotional/sentiment copy.
 * Used in: Mother's Day ("Giving the Best Advice"), Holiday, Valentine's (15% of corpus).
 * Pattern: Image left, emotional text right ("For Doing the Impossible Every Day") + CTA.
 *
 * @param {string} productImage - Product image URL
 * @param {string} productName - Product name
 * @param {string} sentiment - Emotional/sentiment copy (e.g., "For Doing the Impossible Every Day")
 * @param {string} ctaText - CTA text (e.g., "GIFT NOW")
 * @param {string} ctaUrl - CTA URL
 * @param {number} [imageWidth=280] - Product image width
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [sentimentColor="#666666"] - Sentiment text color
 * @param {string} [nameColor="#000000"] - Product name color
 * @param {string} [dividerColor="#e8e2da"] - Bottom divider color
 */
module.exports = function(opts) {
  const productImage = opts.productImage || '';
  const productName = opts.productName || '';
  const sentiment = opts.sentiment || '';
  const ctaText = opts.ctaText || 'GIFT NOW';
  const ctaUrl = opts.ctaUrl || '#';
  const imageWidth = opts.imageWidth || 280;
  const bgColor = opts.bgColor || '#FFFFFF';
  const sentimentColor = opts.sentimentColor || '#666666';
  const nameColor = opts.nameColor || '#000000';
  const dividerColor = opts.dividerColor || '#e8e2da';

  return `
<!-- SENTIMENT PRODUCT ROW -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 0; background-color: ${bgColor};">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px;">
        <tr>
          <!-- Product Image -->
          <td width="${imageWidth}" valign="top" style="padding: 0;">
            <a href="${ctaUrl}" target="_blank">
              <img src="${productImage}" alt="${productName}" width="${imageWidth}" style="display: block; width: ${imageWidth}px; height: auto;" />
            </a>
          </td>
          <!-- Sentiment + CTA -->
          <td width="${600 - imageWidth}" valign="middle" style="padding: 24px 32px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 400; font-style: italic; line-height: 1.4; color: ${sentimentColor}; padding-bottom: 16px;">
                  ${sentiment}
                </td>
              </tr>
              ${productName ? `
              <tr>
                <td style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 700; color: ${nameColor}; padding-bottom: 16px;">
                  ${productName}
                </td>
              </tr>
              ` : ''}
              <tr>
                <td>
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td align="center" style="background-color: #000000;">
                        <a href="${ctaUrl}" target="_blank" style="display: inline-block; padding: 12px 28px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #ffffff; text-decoration: none;">
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
        <!-- Divider -->
        <tr>
          <td colspan="2" style="height: 1px; background-color: ${dividerColor}; font-size: 0; line-height: 0;">&nbsp;</td>
        </tr>
      </table>
    </td>
  </tr>
</table>
<!-- /SENTIMENT PRODUCT ROW -->
`;
};
