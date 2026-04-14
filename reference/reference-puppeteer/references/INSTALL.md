# Puppeteer Skill — VPS Installation

One-time setup. Run these commands on the Paperclip VPS via SSH.

## 1. Install system dependencies

Puppeteer bundles its own Chromium binary, but it requires system libraries on Linux:

```bash
apt-get update && apt-get install -y \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libc6 \
  libcairo2 \
  libcups2 \
  libdbus-1-3 \
  libexpat1 \
  libfontconfig1 \
  libgcc1 \
  libglib2.0-0 \
  libgtk-3-0 \
  libnspr4 \
  libnss3 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libstdc++6 \
  libx11-6 \
  libx11-xcb1 \
  libxcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxi6 \
  libxrandr2 \
  libxrender1 \
  libxss1 \
  libxtst6 \
  ca-certificates \
  fonts-liberation \
  libasound2 \
  libgbm1 \
  libvulkan1 \
  wget \
  xdg-utils
```

## 2. Install npm dependencies

Navigate to the skill's `references/` directory and install:

```bash
cd /path/to/skills/puppeteer/references/
npm install
```

This installs Puppeteer and downloads the Chromium binary (~170MB). Only happens once.

## 3. Verify installation

```bash
node -e "require('puppeteer'); console.log('OK')"
```

Should print `OK`. If it errors, re-run the apt-get step.

## 4. Test a render

```bash
echo "<html><body style='background:red;width:600px;height:100px;'></body></html>" > /tmp/test.html
node references/scripts/slice.js --input /tmp/test.html --output /tmp/ --verbose
```

Should produce `/tmp/test.png` — a 1200×200px red rectangle.

## Troubleshooting

**"error while loading shared libraries"** — re-run the apt-get command above.

**"No usable sandbox"** — the scripts already include `--no-sandbox` for VPS use. If still failing, check that the process user has execute permissions on the Chromium binary.

**Timeout errors** — increase `--timeout` flag. On first run, Chromium may be slower to start. Subsequent runs use the same browser instance and are faster.

**Font not rendering correctly** — ensure the HTML file is complete and self-contained (inline styles, base64 fonts). The script uses `document.fonts.ready` to wait for font loading.
