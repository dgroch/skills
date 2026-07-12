/**
 * comparison-pairs
 *
 * "What I Bought vs What I Got" side-by-side comparison pairs.
 * Used in: UGC emails, Social Proof campaigns.
 * Pattern: Two images side-by-side with "vs" divider, product name below.
 *
 * @param {Object[]} pairs - Array of comparison objects
 *   - leftImage: "What I Bought" image URL
 *   - rightImage: "What I Got" image URL
 *   - productName: Product name (e.g., "Osaka")
 *   - leftLabel: Optional left label (default: "What I Ordered")
 *   - rightLabel: Optional right label (default: "What I Got")
 * @param {string} [sectionTitle] - Optional section title
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [vsText="vs"] - Divider text
 */
module.exports = function(opts) {
  const pairs = opts.pairs || [];
  const sectionTitle = opts.sectionTitle || '';
  const bgColor = opts.bgColor || '#FFFFFF';
  const vsText = opts.vsText || 'vs';

  let pairsHtml = pairs.map(p => {
    const leftLabel = p.leftLabel || 'What I Ordered';
    const rightLabel = p.rightLabel || 'What I Got';
    return `
    <tr>
      <td align="center" style="padding-bottom: 16px;">
        <table role="presentation" width="552" cellpadding="0" cellspacing="0" border="0" style="max-width: 552px;">
          <!-- Labels -->
          <tr>
            <td width="240" align="center" style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #999999; padding-bottom: 8px;">
              ${leftLabel}
            </td>
            <td width="72" align="center"></td>
            <td width="240" align="center" style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #999999; padding-bottom: 8px;">
              ${rightLabel}
            </td>
          </tr>
          <!-- Images -->
          <tr>
            <td width="240" align="center" valign="top">
              <img src="${p.leftImage}" alt="${p.productName} - Ordered" width="240" style="display: block; width: 240px; height: auto;" />
            </td>
            <td width="72" align="center" valign="middle" style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 300; font-style: italic; color: #999999;">
              ${vsText}
            </td>
            <td width="240" align="center" valign="top">
              <img src="${p.rightImage}" alt="${p.productName} - Received" width="240" style="display: block; width: 240px; height: auto;" />
            </td>
          </tr>
          <!-- Product Name -->
          <tr>
            <td colspan="3" align="center" style="padding-top: 12px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 700; color: #000000;">
              ${p.productName}
            </td>
          </tr>
        </table>
      </td>
    </tr>`;
  }).join('');

  return `
<!-- COMPARISON PAIRS -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 32px 24px; background-color: ${bgColor};">
      ${sectionTitle ? `
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 552px;">
        <tr>
          <td align="center" style="padding-bottom: 24px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 22px; font-weight: 700; color: #000000;">
            ${sectionTitle}
          </td>
        </tr>
      </table>
      ` : ''}
      <table role="presentation" width="552" cellpadding="0" cellspacing="0" border="0" style="max-width: 552px;">
        ${pairsHtml}
      </table>
    </td>
  </tr>
</table>
<!-- /COMPARISON PAIRS -->
`;
};
