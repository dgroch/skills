/**
 * Primitive: testimonial
 *
 * Full-width review block with 50% Clay background.
 * Stars, quote text (no quote marks), reviewer attribution.
 * Face2 illustration bottom-right is locked.
 *
 * @param {object} opts
 * @param {string} opts.reviewStars - Star characters (e.g. "★★★★★")
 * @param {string} opts.reviewText - Quote text (no quotation marks)
 * @param {string} opts.reviewerName - Reviewer name and location (e.g. "Emily T., Melbourne")
 * @param {string} [opts.assetsBase] - Base URL for illustration assets
 * @param {string} [opts.illustration] - Illustration name (default: Face2_Black.png)
 * @returns {string} HTML string
 */
module.exports = function renderTestimonial(opts = {}) {
  const {
    reviewStars = '★★★★★',
    reviewText,
    reviewerName,
    assetsBase = '{{ASSETS_BASE}}',
    illustration = 'Face2_Black.png'
  } = opts;

  if (!reviewText) {
    throw new Error('[testimonial] reviewText is required');
  }

  if (!reviewerName) {
    throw new Error('[testimonial] reviewerName is required');
  }

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e8e2da;">
  <tr>
    <td class="sp" align="center" style="padding:48px 64px;background:#EBE5DF;text-align:center;position:relative;overflow:hidden;">
      <!-- ${illustration} illustration — bottom-right, locked -->
      <img src="${assetsBase}/${illustration}" alt="" style="position:absolute;right:-16px;bottom:-20px;height:200px;width:auto;opacity:0.11;display:block;">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:14px;color:#C8A888;letter-spacing:.10em;margin:0 0 20px 0;position:relative;z-index:1;">${reviewStars}</p>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:14px;color:#333333;font-style:italic;line-height:1.8;max-width:400px;margin:0 auto 16px auto;position:relative;z-index:1;">${reviewText}</p>
      <cite style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:11px;letter-spacing:.06em;color:#999999;font-style:normal;display:block;position:relative;z-index:1;">— ${reviewerName}</cite>
    </td>
  </tr>
</table>
</td></tr>`;
};
