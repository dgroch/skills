/**
 * v5-engine: index.js
 *
 * Main entry point for the v5 email pipeline.
 *
 * Usage:
 *   node index.js compose <brief.json> [--theme <name>] [--layout <name>] [--output <path>]
 *   node index.js validate <brief.json>
 *   node index.js render <brief.json> [--format png|pdf] [--output <path>]
 */

// Set Playwright browser path before loading any modules
process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/data/.cache/playwright';

const path = require('path');
const fs = require('fs');
const { compose } = require('./compose');
const { validateBrief, validateOutput } = require('./validate');
const { renderToPng, renderToPdf, isAvailable } = require('./render');

const OUTPUT_DIR = path.join(__dirname, 'output');

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    printUsage();
    process.exit(1);
  }

  switch (command) {
    case 'compose':
      await runCompose(args);
      break;
    case 'validate':
      await runValidate(args);
      break;
    case 'render':
      await runRender(args);
      break;
    case 'pipeline':
      await runPipeline(args);
      break;
    default:
      console.error(`Unknown command: ${command}`);
      printUsage();
      process.exit(1);
  }
}

async function runCompose(args) {
  const briefPath = args[1];
  if (!briefPath) {
    console.error('Usage: compose <brief.json> [--theme <name>] [--layout <name>] [--output <path>]');
    process.exit(1);
  }

  const brief = loadBrief(briefPath);
  const opts = parseFlags(args.slice(2));

  console.log(`\n📧 Composing: ${brief.subject}`);
  console.log(`   Layout: ${opts.layout || brief.layout}`);
  console.log(`   Theme: ${opts.theme || brief.theme}`);

  const result = compose(brief, {
    themeName: opts.theme,
    layoutName: opts.layout
  });

  // Determine output path
  const outputPath = opts.output || path.join(OUTPUT_DIR, `${brief.id}.html`);
  ensureDir(path.dirname(outputPath));
  fs.writeFileSync(outputPath, result.html, 'utf8');

  console.log(`\n✅ Composed successfully`);
  console.log(`   Slots rendered: ${result.meta.slots.filter(s => s.rendered).length}/${result.meta.slots.length}`);
  console.log(`   Output: ${outputPath}`);
  console.log(`   Size: ${(Buffer.byteLength(result.html) / 1024).toFixed(1)}KB`);

  return result;
}

async function runValidate(args) {
  const briefPath = args[1];
  if (!briefPath) {
    console.error('Usage: validate <brief.json>');
    process.exit(1);
  }

  const brief = loadBrief(briefPath);

  console.log(`\n🔍 Validating: ${brief.id}`);

  const briefResult = validateBrief(brief);
  printValidationResult('Brief', briefResult);

  if (!briefResult.valid) {
    process.exit(1);
  }

  // Also validate output if HTML exists
  const htmlPath = path.join(OUTPUT_DIR, `${brief.id}.html`);
  if (fs.existsSync(htmlPath)) {
    const html = fs.readFileSync(htmlPath, 'utf8');
    const { compose } = require('./compose');
    const result = compose(brief);
    const outputResult = validateOutput(html, result.meta);
    printValidationResult('Output', outputResult);
  }

  process.exit(briefResult.valid ? 0 : 1);
}

async function runRender(args) {
  const briefPath = args[1];
  if (!briefPath) {
    console.error('Usage: render <brief.json> [--format png|pdf] [--output <path>]');
    process.exit(1);
  }

  if (!isAvailable()) {
    console.error('❌ Puppeteer not available. Run: npm install puppeteer');
    process.exit(1);
  }

  const brief = loadBrief(briefPath);
  const opts = parseFlags(args.slice(2));
  const format = opts.format || 'png';

  // Compose first
  console.log(`\n🎨 Rendering: ${brief.subject}`);
  const result = compose(brief, {
    themeName: opts.theme,
    layoutName: opts.layout
  });

  const baseName = opts.output || path.join(OUTPUT_DIR, brief.id);

  if (format === 'png') {
    const outputPath = `${baseName}.png`;
    const renderResult = await renderToPng(result.html, { outputPath });
    console.log(`\n✅ Rendered to PNG`);
    console.log(`   Path: ${renderResult.path}`);
    console.log(`   Size: ${renderResult.size.width}x${renderResult.size.height}px`);
  } else {
    const outputPath = `${baseName}.pdf`;
    const renderResult = await renderToPdf(result.html, { outputPath });
    console.log(`\n✅ Rendered to PDF`);
    console.log(`   Path: ${renderResult.path}`);
  }
}

async function runPipeline(args) {
  const briefPath = args[1];
  if (!briefPath) {
    console.error('Usage: pipeline <brief.json> [--theme <name>] [--layout <name>]');
    process.exit(1);
  }

  const brief = loadBrief(briefPath);
  const opts = parseFlags(args.slice(2));

  console.log(`\n🚀 Pipeline: ${brief.id}`);
  console.log('═'.repeat(50));

  // Step 1: Validate
  console.log('\n📋 Step 1: Validate');
  const briefResult = validateBrief(brief);
  printValidationResult('Brief', briefResult);
  if (!briefResult.valid) {
    console.error('\n❌ Pipeline halted: brief validation failed');
    process.exit(1);
  }

  // Step 2: Compose
  console.log('\n📧 Step 2: Compose');
  const result = compose(brief, {
    themeName: opts.theme,
    layoutName: opts.layout
  });

  const htmlPath = path.join(OUTPUT_DIR, `${brief.id}.html`);
  ensureDir(path.dirname(htmlPath));
  fs.writeFileSync(htmlPath, result.html, 'utf8');

  console.log(`   ✅ Composed (${result.meta.slots.filter(s => s.rendered).length} slots)`);

  // Step 3: Validate output
  console.log('\n🔍 Step 3: Validate output');
  const outputResult = validateOutput(result.html, result.meta);
  printValidationResult('Output', outputResult);
  if (!outputResult.valid) {
    console.error('\n❌ Pipeline halted: output validation failed');
    process.exit(1);
  }

  // Step 4: Render (if Puppeteer available)
  if (isAvailable()) {
    console.log('\n🎨 Step 4: Render');
    const pngPath = path.join(OUTPUT_DIR, `${brief.id}.png`);
    const renderResult = await renderToPng(result.html, { outputPath: pngPath });
    console.log(`   ✅ Rendered (${renderResult.size.width}x${renderResult.size.height}px)`);
  } else {
    console.log('\n🎨 Step 4: Render (skipped — Puppeteer not installed)');
  }

  // Summary
  console.log('\n' + '═'.repeat(50));
  console.log('✅ Pipeline complete');
  console.log(`   HTML: ${htmlPath}`);
  console.log(`   Size: ${outputResult.sizeKb}KB`);

  return { html: result.html, meta: result.meta, validation: outputResult };
}

// ── Helpers ──

function loadBrief(briefPath) {
  const resolved = path.resolve(briefPath);
  if (!fs.existsSync(resolved)) {
    console.error(`Brief not found: ${resolved}`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(resolved, 'utf8'));
}

function parseFlags(args) {
  const flags = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      flags[key] = args[i + 1] || true;
      i++;
    }
  }
  return flags;
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function printValidationResult(label, result) {
  if (result.valid) {
    console.log(`   ✅ ${label}: valid`);
  } else {
    console.log(`   ❌ ${label}: ${result.errors.length} error(s)`);
  }
  for (const err of result.errors) {
    console.log(`      ⛔ ${err}`);
  }
  for (const warn of result.warnings) {
    console.log(`      ⚠️  ${warn}`);
  }
}

function printUsage() {
  console.log(`
v5-engine — AI Email Pipeline

Commands:
  compose <brief.json>    Compose HTML from brief
  validate <brief.json>   Validate brief and output
  render <brief.json>     Render to PNG/PDF
  pipeline <brief.json>   Full pipeline (validate → compose → render)

Flags:
  --theme <name>     Override theme
  --layout <name>    Override layout
  --format png|pdf   Render format (default: png)
  --output <path>    Custom output path
  `);
}

main().catch(err => {
  console.error(`\n❌ ${err.message}`);
  process.exit(1);
});
