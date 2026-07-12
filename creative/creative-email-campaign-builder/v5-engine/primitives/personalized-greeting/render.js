/**
 * personalized-greeting
 *
 * Personalized greeting section with Klaviyo variable support.
 * Used in: LTV flows ("Hi {{ first_name }}"), Welcome flows (15% of corpus).
 *
 * @param {string} [greeting="Hi {{ first_name|default:'Moment Maker' }}"] - Greeting with Klaviyo variable
 * @param {string} [bodyText] - Body text following greeting
 * @param {string} [bgColor="#FFFFFF"] - Background color
 * @param {string} [textColor="#333333"] - Text color
 * @param {string} [greetingColor="#000000"] - Greeting color
 */
module.exports = function(opts) {
  const greeting = opts.greeting || "Hi {{ first_name|default:'Moment Maker' }}";
  const bodyText = opts.bodyText || '';
  const bgColor = opts.bgColor || '#FFFFFF';
  const textColor = opts.textColor || '#333333';
  const greetingColor = opts.greetingColor || '#000000';

  return `
<!-- PERSONALIZED GREETING -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 24px 32px; background-color: ${bgColor};">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 536px;">
        <tr>
          <td style="font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 18px; font-weight: 400; line-height: 1.5; color: ${greetingColor};">
            ${greeting}
          </td>
        </tr>
        ${bodyText ? `
        <tr>
          <td style="padding-top: 12px; font-family: 'Neue Haas Grotesk', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; font-weight: 300; line-height: 1.6; color: ${textColor};">
            ${bodyText}
          </td>
        </tr>
        ` : ''}
      </table>
    </td>
  </tr>
</table>
<!-- /PERSONALIZED GREETING -->
`;
};
