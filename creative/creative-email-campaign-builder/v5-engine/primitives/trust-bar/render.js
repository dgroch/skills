/**
 * Primitive: trust-bar
 *
 * Static 5-item trust bar using a single pre-rendered CDN image.
 * Replaces inline SVGs which email clients strip.
 *
 * @param {object} opts
 * @param {string} [opts.imageSrc] - CDN URL for the trust bar image (default: Fig & Bloom CDN)
 * @param {string} [opts.imageAlt] - Alt text describing all 5 USPs
 * @param {string} [opts.href] - Link target (default: "https://figandbloom.com/")
 * @param {string} [opts.background] - Background color (default: #D5D0C4)
 * @returns {string} HTML string
 */
module.exports = function renderTrustBar(opts = {}) {
  const {
    imageSrc = 'https://d3k81ch9hvuctc.cloudfront.net/company/RHSpV7/images/5ee7f699-fa5f-4cf5-9b8c-161b1d44ecfd.png',
    imageAlt = 'Fresh Daily Flowers · Perfect for Every Occasion · Australia-Wide Service · Same Day Delivery · Order Before 1pm',
    href = 'https://figandbloom.com/',
    background = '#D5D0C4'
  } = opts;

  return `<tr><td>
<table border="0" cellpadding="0" cellspacing="0" width="600">
<tr>
<td style="padding:0;background:${background};">
<a href="${href}" style="text-decoration:none;display:block;">
<img alt="${imageAlt}" src="${imageSrc}" style="display:block;outline:none;text-decoration:none;height:auto;font-size:13px;width:100%;" width="600"/>
</a>
</td>
</tr>
</table>
</td></tr>`;
};
