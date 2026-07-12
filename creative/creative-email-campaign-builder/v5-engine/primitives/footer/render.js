/**
 * Primitive: footer
 *
 * Full footer with logo, navigation links, social icons, unsubscribe, and legal.
 * Matches the brand's footer template structure.
 *
 * @param {object} opts
 * @param {string} [opts.logoSrc] - Footer logo image URL
 * @param {string} [opts.logoAlt] - Logo alt text (default: "Fig & Bloom")
 * @param {string} [opts.logoHref] - Logo link (default: "https://figandbloom.com")
 * @param {Array} [opts.links] - Array of { text, href, imageSrc } for nav links (image-based nav supported)
 * @param {Array} [opts.social] - Array of { platform, href, imageSrc } for social icons
 * @param {string} opts.unsubscribeHref - Unsubscribe URL (or use {{ unsubscribe_url }} Klaviyo tag)
 * @param {string} [opts.unsubscribeText] - Unsubscribe anchor text (default: "Unsubscribe")
 * @param {string} [opts.companyName] - Company name (default: "{{ organization.name }}")
 * @param {string} [opts.companyAddress] - Physical address (default: "{{ organization.full_address }}")
 * @param {string} [opts.legal] - Additional legal text
 * @param {string} [opts.background] - Background color (default: #ffffff)
 * @returns {string} HTML string
 */
module.exports = function renderFooter(opts = {}) {
  const {
    logoSrc = '',
    logoAlt = 'Fig & Bloom',
    logoHref = 'https://figandbloom.com',
    links = [],
    social = [],
    unsubscribeHref = '{{ unsubscribe_url }}',
    unsubscribeText = 'Unsubscribe',
    companyName = '{{ organization.name }}',
    companyAddress = '{{ organization.full_address }}',
    legal = '',
    background = '#ffffff'
  } = opts;

  // Logo section
  const logoHtml = logoSrc ? `
<!-- ============ FOOTER LOGO ============ -->
<tr><td>
<table border="0" cellpadding="0" cellspacing="0" width="600">
<tr>
<td style="padding:0;background:${background};">
<a href="${logoHref}" style="text-decoration:none;display:block;">
<img alt="${logoAlt}" src="${logoSrc}" style="display:block;outline:none;text-decoration:none;height:auto;font-size:13px;width:100%;" width="600"/>
</a>
</td>
</tr>
</table>
</td></tr>` : '';

  // Nav links section (supports image-based or text-based)
  let linksHtml = '';
  if (links.length > 0) {
    const linkRows = links.map(link => {
      if (link.imageSrc) {
        return `<tr>
<td style="padding:0;background:${background};">
<a href="${link.href}" style="text-decoration:none;display:block;">
<img alt="${link.text}" src="${link.imageSrc}" style="display:block;outline:none;text-decoration:none;height:auto;font-size:13px;width:100%;" width="600"/>
</a>
</td>
</tr>`;
      }
      return `<tr>
<td align="center" style="padding:4px 0;background:${background};">
<a href="${link.href}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:#000000;text-decoration:none;">${link.text}</a>
</td>
</tr>`;
    }).join('\n');

    linksHtml = `
<!-- ============ FOOTER NAV LINKS ============ -->
<tr><td>
<table border="0" cellpadding="0" cellspacing="0" width="600">
${linkRows}
</table>
</td></tr>`;
  }

  // Social icons section
  let socialHtml = '';
  if (social.length > 0) {
    const colWidth = Math.floor(100 / social.length);
    const socialCells = social.map(s => {
      return `<td align="center" style="width:${colWidth}%;padding:0;">
<a href="${s.href}" style="text-decoration:none;display:block;">
<img alt="${s.platform}" src="${s.imageSrc}" style="display:block;outline:none;text-decoration:none;height:auto;font-size:13px;width:100%;" width="150"/>
</a>
</td>`;
    }).join('\n');

    socialHtml = `
<!-- ============ SOCIAL ICONS ============ -->
<tr><td>
<table border="0" cellpadding="0" cellspacing="0" width="600">
<tr>
<td align="center" style="padding:0;background:${background};">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
${socialCells}
</tr>
</table>
</td>
</tr>
</table>
</td></tr>`;
  }

  // Legal text
  const legalText = legal
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-size:10px;font-weight:300;line-height:1.3;text-align:center;color:#727272;margin:4px 0 0 0;">${legal}</p>`
    : '';

  return `${logoHtml}
${linksHtml}
${socialHtml}

<!-- ============ UNSUBSCRIBE ============ -->
<tr><td>
<table border="0" cellpadding="0" cellspacing="0" width="600">
<tr>
<td align="center" style="padding:9px 18px;background:${background};">
<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-size:10px;font-weight:300;line-height:1.3;text-align:center;color:#727272;margin:0;">No longer want to receive these emails? <a href="${unsubscribeHref}" style="color:#727272;text-decoration:underline;">${unsubscribeText}</a>.</p>
<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-size:10px;font-weight:300;line-height:1.3;text-align:center;color:#727272;margin:4px 0 0 0;">${companyName} ${companyAddress}</p>
${legalText}
</td>
</tr>
</table>
</td></tr>`;
};
