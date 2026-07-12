/**
 * hero-b-white — Text Above Image, White Band
 *
 * Text band (white bg) on top + full-bleed photo (600×360px) below.
 * Illustration BodyFlower_Black anchored right:0, bottom:-30px at 18% opacity.
 *
 * @param {Object} opts
 * @param {string} opts.superLabel   → {{SUPER_LABEL}}     eyebrow label text
 * @param {string} opts.headline     → {{HEADLINE}}         Cervanttis headline (MUST be lowercase)
 * @param {string} opts.subheadline  → {{SUBHEADLINE}}      supporting copy
 * @param {string} opts.ctaText      → {{CTA_TEXT}}         button label
 * @param {string} opts.ctaUrl       → {{CTA_URL}}          button link
 * @param {string} opts.heroImage    → {{HERO_IMAGE_URL}}   photo URL
 * @param {string} [opts.assetsBase] → {{ASSETS_BASE}}      illustration CDN base
 * @returns {string} HTML fragment
 */
module.exports = function renderHeroBWhite(opts) {
  const {
    superLabel = '',
    headline = '',
    subheadline = '',
    ctaText = '',
    ctaUrl = '#',
    heroImage = '',
    assetsBase = 'https://cdn.shopify.com/s/files/1/0657/8723/2489/files/illustrations',
  } = opts;

  let html = `<!-- COMPONENT: heroes/hero-b-white | TEXT ABOVE IMAGE — WHITE BAND
TOKENS: {{SUPER_LABEL}}, {{HEADLINE}} (Cervanttis, lowercase), {{SUBHEADLINE}}, {{CTA_TEXT}}, {{CTA_URL}}, {{HERO_IMAGE_URL}}, {{ASSETS_BASE}}
RULES: Text band top (white bg) + full-bleed photo bottom (600x360). Illustration anchored right:0, bottom:-30px. -->
<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td bgcolor="#ffffff" style="background:#ffffff;padding:48px 48px 40px;text-align:center;position:relative;overflow:hidden;">
      <img src="{{ASSETS_BASE}}/BodyFlower_Black.png" alt="" style="position:absolute;right:0;bottom:-30px;width:220px;height:auto;opacity:0.18;display:block;">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 18px 0;position:relative;z-index:1;">{{SUPER_LABEL}}</p>
      <h1 class="hh" style="font-family:'Cervanttis','Palatino Linotype',Palatino,Georgia,serif;font-weight:400;font-style:normal;font-synthesis:none;-webkit-font-smoothing:antialiased;font-size:54px;color:#000000;line-height:0.95;margin:0 0 16px 0;position:relative;z-index:1;">{{HEADLINE}}</h1>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#666666;max-width:360px;margin:0 auto 28px auto;line-height:1.75;position:relative;z-index:1;">{{SUBHEADLINE}}</p>
      <a href="{{CTA_URL}}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#000000;color:#ffffff;text-decoration:none;padding:14px 40px;display:inline-block;position:relative;z-index:1;">{{CTA_TEXT}}</a>
    </td>
  </tr>
  <tr>
    <td style="padding:0;">
      <img src="{{HERO_IMAGE_URL}}" width="600" height="360" alt="" style="display:block;width:600px;height:360px;object-fit:cover;">
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
  html = html.replace(/\{\{HERO_IMAGE_URL\}\}/g, heroImage);

  return html;
};
