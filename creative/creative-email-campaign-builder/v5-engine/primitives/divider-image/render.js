/**
 * Primitive: divider-image
 *
 * Full-bleed lifestyle image strip divider.
 * Lifestyle photography only — studio shots too static at 180px crop.
 * No text overlay — pure visual pause. Use max once per email.
 *
 * @param {object} opts
 * @param {string} opts.imageUrl - Image URL (minimum 600×360px source)
 * @param {string} [opts.height] - Strip height in px (default: 180, also supports 340)
 * @param {string} [opts.alt] - Image alt text (default: "")
 * @param {string} [opts.objectPosition] - CSS object-position (default: "center 25%")
 * @returns {string} HTML string
 */
module.exports = function renderDividerImage(opts = {}) {
  const {
    imageUrl,
    height = '180',
    alt = '',
    objectPosition = 'center 25%'
  } = opts;

  if (!imageUrl) {
    throw new Error('[divider-image] imageUrl is required');
  }

  return `<tr><td style="padding:0;overflow:hidden;">
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td height="${height}" style="height:${height}px;padding:0;overflow:hidden;">
      <img src="${imageUrl}" width="600" height="${height}" alt="${alt}"
           style="display:block;width:600px;height:${height}px;object-fit:cover;object-position:${objectPosition};">
    </td>
  </tr>
</table>
</td></tr>`;
};
