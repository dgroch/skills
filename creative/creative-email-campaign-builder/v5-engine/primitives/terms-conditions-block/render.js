/**
 * terms-conditions-block
 *
 * Light gray T&C box for sale campaigns.
 * Used in: BFCM, flash sales (40% of Sale emails).
 * Pattern: Light gray background, small text, offer validity details.
 *
 * @param {string} title - Optional title (e.g., "Terms & Conditions")
 * @param {string[]} lines - Array of T&C lines
 * @param {string} [bgColor="#F5F5F5"] - Background color
 * @param {string} [textColor="#999999"] - Text color
 * @param {string} [fontSize=11] - Font size
 * @param {string} [lineHeight=1.6] - Line height
 */
module.exports = function(opts) {
  const title = opts.title || '';
  const lines = opts.lines || [];
  const bgColor = opts.bgColor || '#F5F5F5';
  const textColor = opts.textColor || '#999999';
  const fontSize = opts.fontSize || 11;
  const lineHeight = opts.lineHeight || 1.6;

  const linesHtml = lines.map(line => `<div style="margin-bottom: 4px;">${line}</div>`).join('');

  return `
<!-- TERMS & CONDITIONS BLOCK -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 24px 32px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 536px; background-color: ${bgColor}; border-radius: 0;">
        <tr>
          <td style="padding: 20px 24px;">
            ${title ? `
            <div style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: ${fontSize}px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: ${textColor}; margin-bottom: 8px;">
              ${title}
            </div>
            ` : ''}
            <div style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: ${fontSize}px; font-weight: 300; line-height: ${lineHeight}; color: ${textColor};">
              ${linesHtml}
            </div>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
<!-- /TERMS & CONDITIONS BLOCK -->
`;
};
