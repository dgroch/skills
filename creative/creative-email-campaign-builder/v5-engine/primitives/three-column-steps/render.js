/**
 * Primitive: three-column-steps
 *
 * 3-column numbered steps with configurable background variant.
 * Supports white, clay, 50clay, and beige backgrounds.
 *
 * @param {object} opts
 * @param {string} opts.headline - Lust font headline, sentence case
 * @param {string} opts.step1Number - Step 1 number (e.g. "1.")
 * @param {string} opts.step1Text - Step 1 description
 * @param {string} opts.step2Number - Step 2 number (e.g. "2.")
 * @param {string} opts.step2Text - Step 2 description
 * @param {string} opts.step3Number - Step 3 number (e.g. "3.")
 * @param {string} opts.step3Text - Step 3 description
 * @param {string} opts.ctaText - CTA button text
 * @param {string} opts.ctaUrl - CTA button URL
 * @param {string} [opts.bgVariant] - Background variant: "white" | "clay" | "50clay" | "beige" (default: "white")
 * @param {string} [opts.paddingTop] - Top padding in px (default: "48px")
 * @param {string} [opts.paddingBottom] - Bottom padding in px (default: "48px")
 * @returns {string} HTML string
 */
module.exports = function renderThreeColumnSteps(opts = {}) {
  const {
    headline,
    step1Number = '1.',
    step1Text,
    step2Number = '2.',
    step2Text,
    step3Number = '3.',
    step3Text,
    ctaText = 'Shop Now',
    ctaUrl,
    bgVariant = 'white',
    paddingTop = '48px',
    paddingBottom = '48px'
  } = opts;

  if (!headline) {
    throw new Error('[three-column-steps] headline is required');
  }

  if (!step1Text || !step2Text || !step3Text) {
    throw new Error('[three-column-steps] step1Text, step2Text, and step3Text are required');
  }

  if (!ctaUrl) {
    throw new Error('[three-column-steps] ctaUrl is required');
  }

  // Background color map
  const bgColors = {
    white: '#ffffff',
    clay: '#D8CCBE',
    '50clay': '#EBE5DF',
    beige: '#F5F0EB'
  };

  const bgColor = bgColors[bgVariant] || bgColors.white;

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="${bgColor}">
  <tr>
    <td align="center" style="padding:${paddingTop} 32px 16px;background:${bgColor};">
      <h2 class="sh" style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:26px;color:#000000;line-height:1.2;margin:0 0 36px 0;text-align:center;">${headline}</h2>
    </td>
  </tr>
  <tr>
    <td align="center" style="padding:0 24px 8px;background:${bgColor};">
      <table width="552" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td width="168" valign="top" align="center" style="padding:0 12px 32px;">
            <p style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:40px;color:#000000;margin:0 0 12px 0;line-height:1;">${step1Number}</p>
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#444444;line-height:1.65;margin:0;text-align:center;">${step1Text}</p>
          </td>
          <td width="168" valign="top" align="center" style="padding:0 12px 32px;">
            <p style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:40px;color:#000000;margin:0 0 12px 0;line-height:1;">${step2Number}</p>
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#444444;line-height:1.65;margin:0;text-align:center;">${step2Text}</p>
          </td>
          <td width="168" valign="top" align="center" style="padding:0 12px 32px;">
            <p style="font-family:'Lust',Georgia,'Times New Roman',serif;font-weight:normal;font-style:normal;font-size:40px;color:#000000;margin:0 0 12px 0;line-height:1;">${step3Number}</p>
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#444444;line-height:1.65;margin:0;text-align:center;">${step3Text}</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td align="center" style="padding:0 32px ${paddingBottom};background:${bgColor};">
      <a href="${ctaUrl}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:10px;letter-spacing:.16em;text-transform:uppercase;background:#000000;color:#ffffff;text-decoration:none;padding:14px 40px;display:inline-block;">${ctaText}</a>
    </td>
  </tr>
</table>
</td></tr>`;
};
