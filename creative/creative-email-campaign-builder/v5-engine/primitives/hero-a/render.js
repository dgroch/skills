/**
 * hero-a — Text Over Image
 *
 * Full-width lifestyle image (600×450px), 30% black mask overlay.
 * Headline MUST be lowercase. Cervanttis 56px centered.
 *
 * @param {Object} opts
 * @param {string} opts.superLabel  → {{SUPER_LABEL}}   eyebrow label text
 * @param {string} opts.headline    → {{HEADLINE}}       Cervanttis headline (MUST be lowercase)
 * @param {string} opts.subheadline → {{SUBHEADLINE}}    supporting copy
 * @param {string} opts.ctaText     → {{CTA_TEXT}}       button label
 * @param {string} opts.ctaUrl      → {{CTA_URL}}        button link
 * @param {string} opts.heroImage   → {{HERO_IMAGE_URL}} background image URL
 * @returns {string} HTML fragment
 */
module.exports = function renderHeroA(opts) {
  const {
    superLabel = '',
    headline = '',
    subheadline = '',
    ctaText = '',
    ctaUrl = '#',
    heroImage = '',
  } = opts;

  let html = `<!-- COMPONENT: heroes/hero-a | TEXT OVER IMAGE
TOKENS: {{HERO_IMAGE_URL}}, {{SUPER_LABEL}}, {{HEADLINE}} (Cervanttis, lowercase), {{SUBHEADLINE}}, {{CTA_TEXT}}, {{CTA_URL}}
RULES: 30% black mask overlay. Headline MUST be lowercase. Fixed 450px height. -->
<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td class="ha" valign="middle" style="height:450px;background:url('{{HERO_IMAGE_URL}}') center/cover no-repeat;padding:0;overflow:hidden;position:relative;vertical-align:middle;">
      <div style="position:absolute;inset:0;background:rgba(0,0,0,0.30);"></div>
      <table width="600" cellpadding="0" cellspacing="0" border="0" style="position:relative;z-index:1;">
        <tr>
          <td align="center" style="padding:64px 48px;text-align:center;">
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,0.55);margin:0 0 16px 0;">{{SUPER_LABEL}}</p>
            <h1 class="hh" style="font-family:'Cervanttis','Palatino Linotype',Palatino,Georgia,serif;font-weight:400;font-style:normal;font-synthesis:none;-webkit-font-smoothing:antialiased;font-size:56px;color:#ffffff;line-height:0.95;margin:0 0 20px 0;">{{HEADLINE}}</h1>
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:rgba(255,255,255,0.80);max-width:360px;margin:0 auto 32px auto;line-height:1.75;">{{SUBHEADLINE}}</p>
            <a href="{{CTA_URL}}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#ffffff;color:#000000;text-decoration:none;padding:14px 40px;display:inline-block;">{{CTA_TEXT}}</a>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</td></tr>`;

  html = html.replace(/\{\{HERO_IMAGE_URL\}\}/g, heroImage);
  html = html.replace(/\{\{SUPER_LABEL\}\}/g, superLabel);
  html = html.replace(/\{\{HEADLINE\}\}/g, headline);
  html = html.replace(/\{\{SUBHEADLINE\}\}/g, subheadline);
  html = html.replace(/\{\{CTA_TEXT\}\}/g, ctaText);
  html = html.replace(/\{\{CTA_URL\}\}/g, ctaUrl);

  return html;
};
