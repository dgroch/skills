/**
 * Primitive: header
 *
 * Brand logo centered, 120x24px, with bottom border.
 * Based on Fig & Bloom production header template.
 *
 * @param {object} opts
 * @param {string} opts.logoSrc - URL to logo image (default: Fig & Bloom CDN logo)
 * @param {string} opts.logoAlt - Alt text for logo (default: "Fig & Bloom")
 * @param {string} opts.logoHref - Link target (not used in current template, reserved)
 * @param {number} opts.logoWidth - Logo width in px (default: 120)
 * @param {number} opts.logoHeight - Logo height in px (default: 24)
 * @param {string} opts.background - Background color (default: "#ffffff")
 * @param {string} opts.borderColor - Bottom border color (default: "#e8e2da")
 * @param {string} opts.padding - Cell padding (default: "28px 24px 22px")
 * @param {object} opts.theme - Theme object (injected by compose)
 * @returns {string} HTML string for <tr> row
 */
module.exports = function renderHeader(opts = {}) {
  const {
    logoSrc = 'https://cdn.shopify.com/s/files/1/0657/8723/2489/files/F_B_Logo_Horizontal_BLK_914x200_0eb09d11-e91b-4f05-8ef4-9e54a99cb903.png',
    logoAlt = 'Fig & Bloom',
    logoWidth = 120,
    logoHeight = 24,
    background = '#ffffff',
    borderColor = '#e8e2da',
    padding = '28px 24px 22px',
    theme = {}
  } = opts;

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding:${padding};border-bottom:1px solid ${borderColor};background:${background};">
      <img src="${logoSrc}" width="${logoWidth}" height="${logoHeight}" alt="${logoAlt}" style="width:${logoWidth}px;height:${logoHeight}px;display:inline-block;">
    </td>
  </tr>
</table>
</td></tr>`;
};
