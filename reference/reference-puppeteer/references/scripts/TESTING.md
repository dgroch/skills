# Testing `slice.js` locally

`slice.js` requires `puppeteer` + a Chromium binary. This environment does not ship puppeteer by default, but it does ship `playwright`'s bundled Chromium — we can reuse it.

## One-time setup

```bash
mkdir -p /tmp/slice-test && cd /tmp/slice-test
npm init -y
PUPPETEER_SKIP_DOWNLOAD=true npm install puppeteer minimist
```

`PUPPETEER_SKIP_DOWNLOAD=true` skips the ~300MB Chromium download — we'll point at the existing one.

## Running a slice

```bash
NODE_PATH=/tmp/slice-test/node_modules \
PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome \
node /home/user/skills/reference/reference-puppeteer/references/scripts/slice.js \
  --input  /tmp/slice-test/components \
  --output /tmp/slice-test/slices \
  --assets /home/user/skills/creative/creative-email-campaign-builder/references/assets \
  --width 600 --scale 2 --verbose
```

If the playwright chromium path differs, find it with:

```bash
node -e "console.log(require('/opt/node22/lib/node_modules/playwright').chromium.executablePath())"
```

## Quick component builder

`/tmp/slice-test/build-components.js` (written during the fix-output-quality branch work) assembles filled component HTML from the email-campaign-builder templates so you can iterate without running the full agent pipeline.
