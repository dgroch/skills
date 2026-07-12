/**
 * feedback-request
 *
 * Post-purchase feedback/review request section.
 * Used in: Post-purchase flows ("We'd Love to Hear from You!", email feedback link)
 * Pattern: Warm, personal tone with team member image and simple CTA.
 *
 * @param {string} headline - Headline (e.g., "We'd Love to Hear from You!")
 * @param {string} bodyText - Supporting text
 * @param {string} ctaText - CTA text (e.g., "SHARE YOUR THOUGHTS")
 * @param {string} ctaUrl - CTA URL
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [textColor="#333333"] - Text color
 * @param {string} [teamImageUrl] - Optional team member image URL
 */
module.exports = function(opts) {
  const headline = opts.headline || 'We\'d Love to Hear from You!';
  const bodyText = opts.bodyText || '';
  const ctaText = opts.ctaText || 'SHARE YOUR THOUGHTS';
  const ctaUrl = opts.ctaUrl || '#';
  const bgColor = opts.bgColor || '#FFFFFF';
  const textColor = opts.textColor || '#333333';
  const teamImageUrl = opts.teamImageUrl || '';

  return `
<!-- FEEDBACK REQUEST -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 32px 24px; background-color: ${bgColor};">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 552px;">
        ${teamImageUrl ? `
        <tr>
          <td align="center" style="padding-bottom: 24px;">
            <img src="${teamImageUrl}" alt="Team" width="120" style="display: block; width: 120px; height: 120px; object-fit: cover; border-radius: 50%;" />
          </td>
        </tr>
        ` : ''}
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
        <tr>
          <td align="center" style="padding-top: 24px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="center" style="border: 1.5px solid #000000;">
                  <a href="${ctaUrl}" target="_blank" style="display: inline-block; padding: 12px 32px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #000000; text-decoration: none;">
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
<!-- /FEEDBACK REQUEST -->
`;
};
