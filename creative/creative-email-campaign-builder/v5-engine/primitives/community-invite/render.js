/**
 * community-invite
 *
 * Community/social invite section for post-purchase and retention flows.
 * Used in: Post-purchase ("Connect with Fellow Flower Lovers", Facebook group invite)
 * Pattern: Warm imagery, community-focused copy, soft CTA.
 *
 * @param {string} headline - Headline (e.g., "Connect with Fellow Flower Lovers")
 * @param {string} bodyText - Supporting text
 * @param {string} ctaText - CTA text (e.g., "JOIN THE GROUP")
 * @param {string} ctaUrl - CTA URL
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [textColor="#333333"] - Text color
 * @param {string} [imageUrl] - Optional community image URL
 */
module.exports = function(opts) {
  const headline = opts.headline || '';
  const bodyText = opts.bodyText || '';
  const ctaText = opts.ctaText || 'JOIN THE GROUP';
  const ctaUrl = opts.ctaUrl || '#';
  const bgColor = opts.bgColor || '#FFFFFF';
  const textColor = opts.textColor || '#333333';
  const imageUrl = opts.imageUrl || '';

  return `
<!-- COMMUNITY INVITE -->
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
        ${imageUrl ? `
        <tr>
          <td align="center" style="padding-top: 24px;">
            <img src="${imageUrl}" alt="Community" width="552" style="display: block; max-width: 552px; width: 100%; height: auto;" />
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
<!-- /COMMUNITY INVITE -->
`;
};
