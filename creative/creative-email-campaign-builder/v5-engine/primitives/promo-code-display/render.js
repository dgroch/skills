/**
 * promo-code-display
 *
 * Dashed border promo code box with bold code text.
 * Used in: BFCM, LTV, Welcome flows (30% of corpus emails).
 *
 * @param {string} promoCode - The promo code (e.g., "BFCMBOUQUET2025")
 * @param {string} [label="Use code at checkout"] - Optional label above code
 * @param {string} [ctaText] - Optional CTA button text
 * @param {string} [ctaUrl] - Optional CTA button URL
 * @param {string} [validity] - Optional validity text below code (e.g., "Valid until 28/11/25")
 * @param {string} [bgColor="#FAFAFA"] - Background color
 * @param {string} [borderColor="#e8e2da"] - Dashed border color
 * @param {string} [codeColor="#000000"] - Code text color
 */
module.exports = function(opts) {
  const code = opts.promoCode || '';
  const label = opts.label || 'Use code at checkout';
  const ctaText = opts.ctaText || '';
  const ctaUrl = opts.ctaUrl || '#';
  const validity = opts.validity || '';
  const bgColor = opts.bgColor || '#FAFAFA';
  const borderColor = opts.borderColor || '#e8e2da';
  const codeColor = opts.codeColor || '#000000';

  return `
<!-- PROMO CODE DISPLAY -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 32px 0;">
      <table role="presentation" width="480" cellpadding="0" cellspacing="0" border="0" style="max-width: 480px; width: 100%;">
        <!-- Label -->
        <tr>
          <td align="center" style="padding-bottom: 16px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 12px; font-weight: 400; letter-spacing: 1.5px; text-transform: uppercase; color: #666666;">
            ${label}
          </td>
        </tr>
        <!-- Code Box -->
        <tr>
          <td align="center">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border: 2px dashed ${borderColor}; background-color: ${bgColor};">
              <tr>
                <td align="center" style="padding: 24px 32px;">
                  <!-- Promo Code -->
                  <div style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 24px; font-weight: 700; letter-spacing: 4px; color: ${codeColor}; text-transform: uppercase;">
                    ${code}
                  </div>
                  ${validity ? `
                  <div style="margin-top: 12px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 12px; color: #999999; letter-spacing: 0.5px;">
                    ${validity}
                  </div>
                  ` : ''}
                </td>
              </tr>
            </table>
          </td>
        </tr>
        ${ctaText ? `
        <!-- CTA -->
        <tr>
          <td align="center" style="padding-top: 24px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="center" style="background-color: #000000; border-radius: 0;">
                  <a href="${ctaUrl}" target="_blank" style="display: inline-block; padding: 14px 40px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #ffffff; text-decoration: none;">
                    ${ctaText}
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        ` : ''}
      </table>
    </td>
  </tr>
</table>
<!-- /PROMO CODE DISPLAY -->
`;
};
