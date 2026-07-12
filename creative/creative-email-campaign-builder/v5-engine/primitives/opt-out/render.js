/**
 * Primitive: opt-out
 *
 * Sensitivity opt-out block with 50% Clay background.
 * Cervanttis heading (must be lowercase), gentle tone, outline CTA.
 *
 * @param {object} opts
 * @param {string} opts.optOutHeadline - Cervanttis heading, MUST be lowercase (e.g. "a gentle note")
 * @param {string} opts.optOutBody - 1–2 sentence explanation
 * @param {string} opts.unsubscribeUrl - Unsubscribe URL
 * @param {string} [opts.buttonText] - Button text (default: "Opt Out")
 * @returns {string} HTML string
 */
module.exports = function renderOptOut(opts = {}) {
  const {
    optOutHeadline,
    optOutBody,
    unsubscribeUrl,
    buttonText = 'Opt Out'
  } = opts;

  if (!optOutHeadline) {
    throw new Error('[opt-out] optOutHeadline is required');
  }

  if (!optOutBody) {
    throw new Error('[opt-out] optOutBody is required');
  }

  if (!unsubscribeUrl) {
    throw new Error('[opt-out] unsubscribeUrl is required');
  }

  return `<tr><td>
<table width="600" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e0dbd4;">
  <tr>
    <td class="sp" align="center" style="padding:28px 48px;background:#EBE5DF;text-align:center;border-bottom:1px solid #e0dbd4;">
      <h2 style="font-family:'Cervanttis','Palatino Linotype',Palatino,Georgia,serif;font-weight:400;font-style:normal;font-synthesis:none;-webkit-font-smoothing:antialiased;font-size:22px;color:#000000;margin:0 0 12px 0;">${optOutHeadline}</h2>
      <p style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:300;font-size:12px;color:#666666;line-height:1.7;max-width:380px;margin:0 auto 18px auto;">${optOutBody}</p>
      <a href="${unsubscribeUrl}" style="font-family:'NeuzeitGro','Gill Sans','Gill Sans MT',Calibri,sans-serif;font-weight:700;font-size:9px;letter-spacing:.14em;text-transform:uppercase;background:transparent;color:#000000;text-decoration:none;border:1.5px solid #000000;padding:10px 28px;display:inline-block;">${buttonText}</a>
    </td>
  </tr>
</table>
</td></tr>`;
};
