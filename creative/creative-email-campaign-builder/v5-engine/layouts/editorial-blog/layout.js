/**
 * Layout: editorial-blog
 *
 * Long-form narrative layout inspired by editorial magazines.
 * Optimized for storytelling with generous whitespace and serif typography.
 *
 * Slot order:
 * 1. header
 * 2. hero (image-full or overlay)
 * 3. spacer
 * 4. body (blog narrative)
 * 5. divider
 * 6. product (single or dual, tied to narrative)
 * 7. spacer
 * 8. cta (primary + secondary)
 * 9. spacer
 * 10. body (closing note, optional)
 * 11. divider
 * 12. footer
 */

const PRIMITIVE_ORDER = [
  'header',
  'hero',
  'spacer',
  'body',
  'divider',
  'product',
  'spacer',
  'cta',
  'spacer',
  'body',
  'divider',
  'footer'
];

const DEFAULT_SLOT_CONFIG = {
  header: {
    required: true,
    defaults: { align: 'center', logoHeight: 28 }
  },
  hero: {
    required: true,
    defaults: { variant: 'image-full', imageHeight: 360 }
  },
  'spacer-1': { primitive: 'spacer', defaults: { height: 40 } },
  'body-main': { primitive: 'body', required: true, defaults: { maxWidth: '520px' } },
  'divider-1': { primitive: 'divider', defaults: { padding: '0 48px' } },
  product: {
    required: false,
    defaults: { layout: 'dual', padding: '32px 48px' }
  },
  'spacer-2': { primitive: 'spacer', defaults: { height: 32 } },
  cta: {
    required: true,
    defaults: { align: 'center', padding: '24px 48px' }
  },
  'spacer-3': { primitive: 'spacer', defaults: { height: 32 } },
  'body-closing': { primitive: 'body', required: false, defaults: { maxWidth: '520px' } },
  'divider-2': { primitive: 'divider', defaults: { padding: '0 48px' } },
  footer: {
    required: true,
    defaults: { padding: '32px 48px' }
  }
};

/**
 * Get the layout slot order and defaults
 */
function getLayoutSpec() {
  return {
    name: 'editorial-blog',
    slots: PRIMITIVE_ORDER,
    slotConfig: DEFAULT_SLOT_CONFIG,
    constraints: {
      maxWidth: 600,
      backgroundColor: 'theme.background',
      requiredSlots: ['header', 'hero', 'body-main', 'cta', 'footer']
    }
  };
}

module.exports = { getLayoutSpec, PRIMITIVE_ORDER, DEFAULT_SLOT_CONFIG };
