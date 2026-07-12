/**
 * hero-c2-clay — Split Hero, Text Left / Image Right, Clay
 *
 * 50/50 split (300+300), fixed 440px height.
 * Clay (#D8CCBE) text column left, photo right.
 * Illustration HandRose_White at right:-16px, bottom:-20px, opacity 15%.
 * Text col has border-right (not border-left).
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
module.exports = function renderHeroC2Clay(opts) {
  const {
    superLabel = '',
    headline = '',
    subheadline = '',
    ctaText = '',
    ctaUrl = '#',
    heroImage = '',
    assetsBase = 'https://cdn.shopify.com/s/files/1/0657/8723/2489/files/illustrations',
  } = opts;

  let html = `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td class="hc" width="300" valign="middle" style="width:300px;height:440px;background:#D8CCBE;padding:40px 36px;vertical-align:middle;position:relative;overflow:hidden;border-left:none;border-right:1px solid #e8e2da;">
      <img src="{{ASSETS_BASE}}/HandRose_White.png" width="auto" alt="" style="position:absolute;right:-16px;bottom:-20px;height:262px;width:auto;opacity:0.15;display:block;">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#8a8078;margin:0 0 20px 0;position:relative;z-index:1;">{{SUPER_LABEL}}</p>
      <h1 class="hh" style="font-family:'Cervanttis','Palatino Linotype',Palatino,Georgia,serif;font-weight:400;font-style:normal;font-synthesis:none;-webkit-font-smoothing:antialiased;font-size:44px;color:#000000;line-height:1.0;margin:0 0 18px 0;text-align:left;position:relative;z-index:1;">{{HEADLINE}}</h1>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:12px;color:#4a443e;line-height:1.75;margin:0 0 28px 0;text-align:left;max-width:190px;position:relative;z-index:1;">{{SUBHEADLINE}}</p>
      <a href="{{CTA_URL}}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#000000;color:#ffffff;text-decoration:none;padding:13px 24px;display:inline-block;position:relative;z-index:1;">{{CTA_TEXT}}</a>
    </td><td class="hc" width="300" valign="top" style="width:300px;height:440px;padding:0;overflow:hidden;vertical-align:top;">
      <img src="{{HERO_IMAGE_URL}}" width="300" height="440" alt="" style="display:block;width:300px;height:440px;object-fit:cover;object-position:center top;">
    </td>
  </tr>
</table>
</td></tr>`;

  html = html.replace(/\{\{ASSETS_BASE\}\}/g, assetsBase);
  html = html.replace(/\{\{HERO_IMAGE_URL\}\}/g, heroImage);
  html = html.replace(/\{\{SUPER_LABEL\}\}/g, superLabel);
  html = html.replace(/\{\{HEADLINE\}\}/g, headline);
  html = html.replace(/\{\{SUBHEADLINE\}\}/g, subheadline);
  html = html.replace(/\{\{CTA_TEXT\}\}/g, ctaText);
  html = html.replace(/\{\{CTA_URL\}\}/g, ctaUrl);

  return html;
};
