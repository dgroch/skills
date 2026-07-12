/**
 * v5-engine: validate.js
 *
 * Pre-flight validation for briefs and composed output.
 */

const BANNED_WORDS = ['elevate', 'curate', 'stunning', 'gorgeous', 'pop of colour', "don't miss out"];
const MAX_SUBJECT_LENGTH = 50;

/**
 * Validate a brief before composition
 * @param {object} brief - Brief JSON
 * @returns {{ valid: boolean, errors: string[], warnings: string[] }}
 */
function validateBrief(brief) {
  const errors = [];
  const warnings = [];

  // Required fields
  if (!brief.id) errors.push('Missing required field: id');
  if (!brief.campaignDate) errors.push('Missing required field: campaignDate');
  if (!brief.layout) errors.push('Missing required field: layout');
  if (!brief.theme) errors.push('Missing required field: theme');
  if (!brief.subject) errors.push('Missing required field: subject');
  if (!brief.primaryCta) errors.push('Missing required field: primaryCta');

  // Subject length
  if (brief.subject && brief.subject.length > MAX_SUBJECT_LENGTH) {
    errors.push(`Subject line exceeds ${MAX_SUBJECT_LENGTH} chars (${brief.subject.length})`);
  }

  // Preview text
  if (!brief.preview) {
    warnings.push('No preview text provided');
  }

  // Banned words check
  const copyGuardrails = brief.copyGuardrails || {};
  const bannedList = copyGuardrails.banned || BANNED_WORDS;
  const allText = [
    brief.subject,
    brief.preview,
    brief.primaryCta?.text,
    brief.secondaryCta?.text
  ].filter(Boolean).join(' ').toLowerCase();

  for (const word of bannedList) {
    if (allText.includes(word.toLowerCase())) {
      errors.push(`Banned word found: "${word}"`);
    }
  }

  // Emoji check
  if (copyGuardrails.emoji === false) {
    const emojiRegex = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
    if (emojiRegex.test(allText)) {
      errors.push('Emoji detected but emoji=false in guardrails');
    }
  }

  // CTA validation
  if (brief.primaryCta) {
    if (!brief.primaryCta.text) errors.push('primaryCta missing text');
    if (!brief.primaryCta.href) errors.push('primaryCta missing href');
  }
  if (brief.secondaryCta) {
    if (!brief.secondaryCta.text) warnings.push('secondaryCta missing text');
    if (!brief.secondaryCta.href) warnings.push('secondaryCta missing href');
  }

  // Date validation
  if (brief.campaignDate) {
    const date = new Date(brief.campaignDate);
    if (isNaN(date.getTime())) {
      errors.push(`Invalid campaignDate: ${brief.campaignDate}`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Validate composed HTML output
 * @param {string} html - Composed HTML
 * @param {object} meta - Composition metadata
 * @returns {{ valid: boolean, errors: string[], warnings: string[] }}
 */
function validateOutput(html, meta) {
  const errors = [];
  const warnings = [];

  if (!html || html.length === 0) {
    errors.push('Empty HTML output');
    return { valid: false, errors, warnings };
  }

  // Check for required HTML structure
  if (!html.includes('<!DOCTYPE html>')) {
    errors.push('Missing DOCTYPE declaration');
  }
  if (!html.includes('<html')) {
    errors.push('Missing <html> tag');
  }
  if (!html.includes('</html>')) {
    errors.push('Missing closing </html> tag');
  }

  // Check for MSO conditionals (Outlook compatibility)
  if (!html.includes('[if mso]')) {
    warnings.push('No MSO conditional comments found — Outlook rendering may be affected');
  }

  // Check for viewport meta
  if (!html.includes('viewport')) {
    warnings.push('Missing viewport meta tag');
  }

  // Check slot rendering from meta
  if (meta && meta.slots) {
    const failedSlots = meta.slots.filter(s => !s.rendered && !s.error?.includes('not found'));
    if (failedSlots.length > 0) {
      warnings.push(`Slots not rendered: ${failedSlots.map(s => s.slot).join(', ')}`);
    }

    const errorSlots = meta.slots.filter(s => s.error);
    if (errorSlots.length > 0) {
      warnings.push(`Slots with errors: ${errorSlots.map(s => `${s.slot}: ${s.error}`).join('; ')}`);
    }
  }

  // Check for broken image tags
  const imgTags = html.match(/<img[^>]*>/gi) || [];
  for (const img of imgTags) {
    if (!img.includes('src="')) {
      errors.push(`Image tag missing src attribute`);
    }
    if (!img.includes('alt=')) {
      warnings.push(`Image tag missing alt attribute`);
    }
  }

  // Check for unclosed tags (basic check)
  const openTags = (html.match(/<table/gi) || []).length;
  const closeTags = (html.match(/<\/table>/gi) || []).length;
  if (openTags !== closeTags) {
    errors.push(`Mismatched table tags: ${openTags} open, ${closeTags} close`);
  }

  // Size check
  const sizeKb = Buffer.byteLength(html, 'utf8') / 1024;
  if (sizeKb > 102) {
    warnings.push(`HTML size (${sizeKb.toFixed(1)}KB) exceeds 102KB — may trigger Gmail clipping`);
  }
  if (sizeKb > 200) {
    errors.push(`HTML size (${sizeKb.toFixed(1)}KB) exceeds 200KB — too large for most ESPs`);
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    sizeKb: sizeKb.toFixed(1)
  };
}

module.exports = { validateBrief, validateOutput, BANNED_WORDS, MAX_SUBJECT_LENGTH };
