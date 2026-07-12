/**
 * countdown-timer
 *
 * Visual countdown timer with DAYS / HOURS / MINUTES circular blocks.
 * Used in: LTV flows, Giveaway campaigns, Easter urgency (20% of corpus).
 * Confirmed pattern: "14 DAYS 0 HOURS 0 MINUTES" in white circles.
 *
 * @param {string} days - Number of days (e.g., "14")
 * @param {string} hours - Number of hours (e.g., "0")
 * @param {string} minutes - Number of minutes (e.g., "0")
 * @param {string} [label="Offer expires in"] - Optional label above timer
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [circleBg="#000000"] - Circle background color
 * @param {string} [circleColor="#FFFFFF"] - Text color inside circles
 * @param {string} [labelColor="#666666"] - Label text color
 * @param {string} [separatorLabel="DAYS"] - Label after first number
 * @param {string} [separatorLabel2="HOURS"] - Label after second number
 * @param {string} [separatorLabel3="MINUTES"] - Label after third number
 */
module.exports = function(opts) {
  const days = opts.days || '0';
  const hours = opts.hours || '0';
  const minutes = opts.minutes || '0';
  const label = opts.label || '';
  const bgColor = opts.bgColor || '#FFFFFF';
  const circleBg = opts.circleBg || '#000000';
  const circleColor = opts.circleColor || '#FFFFFF';
  const labelColor = opts.labelColor || '#666666';
  const sep1 = opts.separatorLabel || 'DAYS';
  const sep2 = opts.separatorLabel2 || 'HOURS';
  const sep3 = opts.separatorLabel3 || 'MINUTES';

  // Circular block size
  const size = 64;
  const fontSize = 22;

  function circle(num, label) {
    return `
    <td align="center" valign="top" style="padding: 0 8px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td align="center" width="${size}" height="${size}" style="width: ${size}px; height: ${size}px; border-radius: 50%; background-color: ${circleBg}; text-align: center; vertical-align: middle; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: ${fontSize}px; font-weight: 700; color: ${circleColor}; line-height: ${size}px;">
            ${num}
          </td>
        </tr>
        <tr>
          <td align="center" style="padding-top: 8px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 9px; font-weight: 700; letter-spacing: 2px; color: ${labelColor}; text-transform: uppercase;">
            ${label}
          </td>
        </tr>
      </table>
    </td>`;
  }

  return `
<!-- COUNTDOWN TIMER -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 24px 0; background-color: ${bgColor};">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0">
        ${label ? `
        <tr>
          <td align="center" style="padding-bottom: 16px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 12px; font-weight: 400; letter-spacing: 1.5px; color: ${labelColor}; text-transform: uppercase;">
            ${label}
          </td>
        </tr>
        ` : ''}
        <tr>
          ${circle(days, sep1)}
          ${circle(hours, sep2)}
          ${circle(minutes, sep3)}
        </tr>
      </table>
    </td>
  </tr>
</table>
<!-- /COUNTDOWN TIMER -->
`;
};
