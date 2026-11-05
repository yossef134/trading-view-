// Render the audit HTML to an A4 PDF with Playwright (Chromium).
// usage: node render_pdf.js <in.html> <out.pdf> [--png <out-prefix>]
// If `require('playwright')` fails, run with NODE_PATH=$(npm root -g).
let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) { ({ chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright')); }

(async () => {
  const [inp, out] = process.argv.slice(2);
  const pngIdx = process.argv.indexOf('--png');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 794, height: 1123 } });
  await page.goto('file://' + inp, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: out, format: 'A4', printBackground: true, margin: { top: 0, bottom: 0, left: 0, right: 0 } });
  if (pngIdx > -1) {
    const prefix = process.argv[pngIdx + 1];
    const pages = await page.$$('section.page');
    for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: `${prefix}-${i + 1}.png` });
  }
  console.log(`pdf -> ${out}`);
  await browser.close();
})();
