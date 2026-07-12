/**
 * Primitive: delivery-cutoffs
 *
 * Two-column delivery cutoff dates section.
 * White background with region/time rows and optional note.
 *
 * @param {object} opts
 * @param {string} opts.region1 - First region name (e.g. "Metro Melbourne")
 * @param {string} opts.cutoff1 - First cutoff text (e.g. "Order by 1pm Thursday May 8")
 * @param {string} opts.region2 - Second region name (e.g. "Regional Victoria")
 * @param {string} opts.cutoff2 - Second cutoff text (e.g. "Order by 1pm Monday May 5")
 * @param {string} [opts.cutoffNote] - Additional note text
 * @param {string} [opts.headingText] - Section heading (default: "Order Deadlines")
 * @returns {string} HTML string
 */
module.exports = function renderDeliveryCutoffs(opts = {}) {
  const {
    region1,
    cutoff1,
    region2,
    cutoff2,
    cutoffNote = '',
    headingText = 'Order Deadlines'
  } = opts;

  if (!region1 || !cutoff1) {
    throw new Error('[delivery-cutoffs] region1 and cutoff1 are required');
  }

  if (!region2 || !cutoff2) {
    throw new Error('[delivery-cutoffs] region2 and cutoff2 are required');
  }

  const noteHtml = cutoffNote
    ? `<p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:11px;color:#aaaaaa;margin:18px 0 0 0;">${cutoffNote}</p>`
    : '';

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e8e2da;">
  <tr>
    <td class="sp" align="center" style="padding:36px 48px;background:#ffffff;text-align:center;">
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#aaaaaa;margin:0 0 20px 0;">${headingText}</p>
      <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td class="cc" width="50%" align="center" style="width:50%;padding:0 20px 0 0;border-right:1px solid #e8e2da;vertical-align:top;">
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:11px;color:#000000;letter-spacing:.04em;margin:0 0 4px 0;">${region1}</p>
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#444444;line-height:1.6;margin:0;">${cutoff1}</p>
          </td>
          <td class="cc" width="50%" align="center" style="width:50%;padding:0 0 0 20px;vertical-align:top;">
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:11px;color:#000000;letter-spacing:.04em;margin:0 0 4px 0;">${region2}</p>
            <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:13px;color:#444444;line-height:1.6;margin:0;">${cutoff2}</p>
          </td>
        </tr>
      </table>
      ${noteHtml}
    </td>
  </tr>
</table>
</td></tr>`;
};
