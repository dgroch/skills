/**
 * hero-image-only — Full-Width Image, No Text
 *
 * Full-bleed image block with optional link wrapping.
 * No text overlay, no headline, no button — image tells the story.
 * 4:5 aspect ratio (600×750px display). Includes MSO VML fallback.
 *
 * @param {Object} opts
 * @param {string} opts.heroImage   → {{HERO_IMAGE_URL}}   image URL
 * @param {string} opts.imageAlt    → {{HERO_IMAGE_ALT}}    alt text (accessibility)
 * @param {string} [opts.heroLinkUrl] → {{HERO_LINK_URL}}   optional href wrapping the image
 * @returns {string} HTML fragment
 */
module.exports = function renderHeroImageOnly(opts) {
  const {
    heroImage = '',
    imageAlt = '',
    heroLinkUrl = '#',
  } = opts;

  let html = `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff">
  <tr>
    <td align="center" valign="top" style="padding:0;background:#ffffff;">
      <a href="{{HERO_LINK_URL}}" style="display:block;line-height:0;font-size:0;text-decoration:none;" target="_blank">
        <!--[if gte mso 9]>
        <v:image xmlns:v="urn:schemas-microsoft-com:vml"
          src="{{HERO_IMAGE_URL}}"
          style="width:600px;height:750px;"
          cropbottom="0" cropleft="0" cropright="0" croptop="0"/>
        <![endif]-->
        <!--[if !gte mso 9]><!-->
        <img src="{{HERO_IMAGE_URL}}"
             alt="{{HERO_IMAGE_ALT}}"
             width="600"
             height="750"
             border="0"
             style="display:block;width:100%;max-width:600px;height:auto;object-fit:cover;object-position:center;" />
        <!--<![endif]-->
      </a>
    </td>
  </tr>
</table>
</td></tr>`;

  html = html.replace(/\{\{HERO_IMAGE_URL\}\}/g, heroImage);
  html = html.replace(/\{\{HERO_IMAGE_ALT\}\}/g, imageAlt);
  html = html.replace(/\{\{HERO_LINK_URL\}\}/g, heroLinkUrl);

  return html;
};
