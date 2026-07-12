/**
 * Primitive: divider-illustration
 *
 * Illustration strip divider with configurable background and illustration.
 * Uses CSS background-image with the _wide variant of illustrations.
 * 35% crop shows blooms. Height 120px locked.
 *
 * @param {object} opts
 * @param {string} [opts.illustration] - Illustration name without suffix (default: "BodyFlower")
 *   Supported: BodyFlower, Body, Face1, Face2, FrontFace, HandFlower, HandPlant, HandRose
 * @param {string} [opts.bgVariant] - Background variant: "white" | "clay" | "50clay" | "noir" (default: "white")
 * @param {string} [opts.color] - Illustration color: "White" | "Black" (default: auto based on bgVariant)
 * @param {string} [opts.assetsBase] - Base URL for illustration assets (default: '{{ASSETS_BASE}}')
 * @param {string} [opts.showBorders] - Show top/bottom border (default: true for white, false for others)
 * @returns {string} HTML string
 */
module.exports = function renderDividerIllustration(opts = {}) {
  const {
    illustration = 'BodyFlower',
    bgVariant = 'white',
    color,
    assetsBase = '{{ASSETS_BASE}}',
    showBorders
  } = opts;

  // Background color map
  const bgColors = {
    white: '#ffffff',
    clay: '#D8CCBE',
    '50clay': '#EBE5DF',
    noir: '#000000'
  };

  const bgColor = bgColors[bgVariant] || bgColors.white;

  // Auto-determine illustration color based on background
  // White bg → Black illustration (or as specified in templates: BodyFlower_White_wide.png is used across all)
  // The source templates all use BodyFlower_White_wide.png regardless of bg color
  const illustrationColor = color || 'White';
  const imageName = `${illustration}_${illustrationColor}_wide.png`;
  const imageUrl = `${assetsBase}/${imageName}`;

  // Border handling: white variant has borders in the source template
  const useBorder = showBorders !== undefined ? showBorders : (bgVariant === 'white');
  const borderStyle = useBorder ? 'border-top:1px solid #e8e2da;border-bottom:1px solid #e8e2da;' : '';

  return `<tr><td${borderStyle ? ` style="${borderStyle}"` : ''}>
<table width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="${bgColor}">
  <tr>
    <td height="120" bgcolor="${bgColor}"
      background="${imageUrl}"
      style="height:120px;min-height:120px;max-height:120px;background-color:${bgColor};background-image:url('${imageUrl}');background-size:130%;background-position:center 30%;background-repeat:no-repeat;overflow:hidden;line-height:120px;font-size:0;">&nbsp;</td>
  </tr>
</table>
</td></tr>`;
};
