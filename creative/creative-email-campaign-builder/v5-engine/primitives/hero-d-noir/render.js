/**
 * hero-d-noir — Dark Hero, Type-Forward, No Photo, Noir
 *
 * No photography — type and flanking illustrations only.
 * Fixed 500px height. Noir (#000) bg.
 * Flanking HandRose_White illustrations at height:410px, opacity 30%/25%.
 * Cervanttis headline 62px, MUST be lowercase.
 *
 * @param {Object} opts
 * @param {string} opts.superLabel   → {{SUPER_LABEL}}     eyebrow label text
 * @param {string} opts.headline     → {{HEADLINE}}         Cervanttis headline (MUST be lowercase)
 * @param {string} opts.subheadline  → {{SUBHEADLINE}}      supporting copy
 * @param {string} opts.ctaText      → {{CTA_TEXT}}         button label
 * @param {string} opts.ctaUrl       → {{CTA_URL}}          button link
 * @param {string} [opts.assetsBase] → {{ASSETS_BASE}}      illustration CDN base
 * @returns {string} HTML fragment
 */
module.exports = function renderHeroDNoir(opts) {
  const {
    superLabel = '',
    headline = '',
    subheadline = '',
    ctaText = '',
    ctaUrl = '#',
    assetsBase = 'https://cdn.shopify.com/s/files/1/0657/8723/2489/files/illustrations',
  } = opts;

  let html = `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="#000000">
  <tr>
    <td class="ud" align="center" valign="middle" bgcolor="#000000"
        style="background:#000000;height:500px;padding:72px 64px;text-align:center;position:relative;overflow:hidden;vertical-align:middle;">
      <!-- Illustration left — HandFlower, bottom-anchored, 410px total (350 visible + 60 bleed) -->
      <img src="{{ASSETS_BASE}}/HandRose_White.png" alt="" style="position:absolute;left:-16px;bottom:-60px;height:410px;width:auto;opacity:0.30;display:block;">
      <!-- Illustration right — HandRose mirrored -->
      <img src="{{ASSETS_BASE}}/HandRose_White.png" alt="" style="position:absolute;right:-16px;bottom:-60px;height:410px;width:auto;opacity:0.25;display:block;transform:scaleX(-1);">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,0.40);margin:0 0 24px 0;position:relative;z-index:1;">{{SUPER_LABEL}}</p>
      <h1 class="uh" style="font-family:'Cervanttis','Palatino Linotype',Palatino,Georgia,serif;font-weight:400;font-style:normal;font-synthesis:none;-webkit-font-smoothing:antialiased;font-size:62px;color:#ffffff;line-height:0.95;margin:0 0 20px 0;position:relative;z-index:1;">{{HEADLINE}}</h1>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:rgba(255,255,255,0.70);max-width:300px;margin:0 auto 32px auto;line-height:1.75;position:relative;z-index:1;">{{SUBHEADLINE}}</p>
      <a href="{{CTA_URL}}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#ffffff;color:#000000;text-decoration:none;padding:14px 40px;display:inline-block;position:relative;z-index:1;">{{CTA_TEXT}}</a>
    </td>
  </tr>
</table>
</td></tr>`;

  html = html.replace(/\{\{ASSETS_BASE\}\}/g, assetsBase);
  html = html.replace(/\{\{SUPER_LABEL\}\}/g, superLabel);
  html = html.replace(/\{\{HEADLINE\}\}/g, headline);
  html = html.replace(/\{\{SUBHEADLINE\}\}/g, subheadline);
  html = html.replace(/\{\{CTA_TEXT\}\}/g, ctaText);
  html = html.replace(/\{\{CTA_URL\}\}/g, ctaUrl);

  return html;
};
