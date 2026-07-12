/**
 * product-grid
 *
 * Multi-column product grid (2-4 products per row) with optional discount badges.
 * Used in: BFCM, Product Launch, Christmas Gift Guide, Giveaway (20% of corpus).
 * Pattern: Products in grid rows, each with image + name + CTA.
 *
 * @param {Object[]} products - Array of product objects
 *   - image: Product image URL
 *   - name: Product name
 *   - price: Product price (optional)
 *   - url: Product URL
 *   - ctaText: CTA text (default: "SHOP NOW")
 *   - badge: Optional discount badge text (e.g., "20% OFF")
 * @param {number} [columns=2] - Number of columns (2, 3, or 4)
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [sectionTitle] - Optional section title above grid
 * @param {string} [ctaBg="#000000"] - CTA button background
 * @param {string} [ctaColor="#FFFFFF"] - CTA button text color
 */
module.exports = function(opts) {
  const products = opts.products || [];
  const columns = opts.columns || 2;
  const bgColor = opts.bgColor || '#FFFFFF';
  const sectionTitle = opts.sectionTitle || '';
  const ctaBg = opts.ctaBg || '#000000';
  const ctaColor = opts.ctaColor || '#FFFFFF';

  const colWidth = Math.floor(552 / columns);
  const gutter = columns > 2 ? 8 : 16;

  let rowsHtml = '';
  for (let i = 0; i < products.length; i += columns) {
    const rowProducts = products.slice(i, i + columns);
    let cellsHtml = rowProducts.map((p, idx) => {
      const badgeHtml = p.badge ? `
        <tr>
          <td align="center" style="padding-bottom: 8px;">
            <span style="display: inline-block; padding: 4px 10px; background-color: #000000; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #FFFFFF;">
              ${p.badge}
            </span>
          </td>
        </tr>
      ` : '';

      return `
      <td width="${colWidth}" valign="top" style="padding: 0 ${gutter / 2}px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
          ${badgeHtml}
          <tr>
            <td align="center" style="padding-bottom: 12px;">
              <a href="${p.url || '#'}" target="_blank">
                <img src="${p.image}" alt="${p.name}" width="${colWidth - gutter}" style="display: block; width: ${colWidth - gutter}px; height: auto;" />
              </a>
            </td>
          </tr>
          <tr>
            <td align="center" style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 700; color: #000000; padding-bottom: 4px;">
              ${p.name}
            </td>
          </tr>
          ${p.price ? `
          <tr>
            <td align="center" style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; font-weight: 300; color: #666666; padding-bottom: 12px;">
              ${p.price}
            </td>
          </tr>
          ` : ''}
          <tr>
            <td align="center" style="padding-bottom: ${i + columns < products.length ? '24px' : '0'};">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="background-color: ${ctaBg};">
                    <a href="${p.url || '#'}" target="_blank" style="display: inline-block; padding: 10px 20px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: ${ctaColor}; text-decoration: none;">
                      ${p.ctaText || 'SHOP NOW'}
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>`;
    }).join('');

    rowsHtml += `
    <tr>
      ${cellsHtml}
    </tr>`;
  }

  return `
<!-- PRODUCT GRID -->
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
        ${rowsHtml}
      </table>
    </td>
  </tr>
</table>
<!-- /PRODUCT GRID -->
`;
};
