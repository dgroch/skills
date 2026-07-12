/**
 * giveaway-banner
 *
 * Giveaway/prize display with value amounts and countdown.
 * Used in: Giveaway campaigns (100% of Giveaway emails).
 * Pattern: Prize value display, countdown timer, "Shop to Enter" CTA.
 *
 * @param {string} headline - Main headline (e.g., "Win a $200 Voucher")
 * @param {string} bodyText - Supporting text
 * @param {string} ctaText - CTA text (e.g., "SHOP TO ENTER")
 * @param {string} ctaUrl - CTA URL
 * @param {string} [prizeValue] - Prize value display (e.g., "$200")
 * @param {string} [prizeDescription] - Prize description (e.g., "Fig & Bloom Gift Voucher")
 * @param {Object} [countdown] - Optional countdown timer opts (days, hours, minutes)
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [accentColor="#000000"] - Accent color for prize value
 */
module.exports = function(opts) {
  const headline = opts.headline || '';
  const bodyText = opts.bodyText || '';
  const ctaText = opts.ctaText || 'SHOP TO ENTER';
  const ctaUrl = opts.ctaUrl || '#';
  const prizeValue = opts.prizeValue || '';
  const prizeDescription = opts.prizeDescription || '';
  const countdown = opts.countdown || null;
  const bgColor = opts.bgColor || '#FFFFFF';
  const accentColor = opts.accentColor || '#000000';

  let countdownHtml = '';
  if (countdown) {
    const c = require('./countdown-timer/render.js')(countdown);
    countdownHtml = c;
  }

  const prizeHtml = prizeValue ? `
    <tr>
      <td align="center" style="padding-top: 16px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td align="center" style="background-color: ${accentColor}; padding: 16px 32px;">
              <span style="display: inline-block; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 36px; font-weight: 700; color: #ffffff;">
                ${prizeValue}
              </span>
            </td>
          </tr>
        </table>
        ${prizeDescription ? `
        <div style="margin-top: 8px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; font-weight: 400; color: #666666;">
          ${prizeDescription}
        </div>
        ` : ''}
      </td>
    </tr>
  ` : '';

  return `
<!-- GIVEAWAY BANNER -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 32px 24px; background-color: ${bgColor};">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 552px;">
        <tr>
          <td align="center" style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 28px; font-weight: 700; line-height: 1.2; color: ${accentColor};">
            ${headline}
          </td>
        </tr>
        ${bodyText ? `
        <tr>
          <td align="center" style="padding-top: 12px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 300; line-height: 1.6; color: #666666;">
            ${bodyText}
          </td>
        </tr>
        ` : ''}
        ${prizeHtml}
        ${countdownHtml ? `
        <tr>
          <td align="center" style="padding-top: 24px;">
            ${countdownHtml}
          </td>
        </tr>
        ` : ''}
        <tr>
          <td align="center" style="padding-top: 24px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="center" style="background-color: ${accentColor};">
                  <a href="${ctaUrl}" target="_blank" style="display: inline-block; padding: 14px 40px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #ffffff; text-decoration: none;">
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
<!-- /GIVEAWAY BANNER -->
`;
};
