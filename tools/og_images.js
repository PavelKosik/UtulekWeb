// Vygeneruje náhledové obrázky pro sdílení (1200×630) a ikony webu.
// Spuštění:  node tools/og_images.js   (potřebuje Playwright: npm i -D playwright && npx playwright install chromium)
// Čísla a texty berte z tools/build.py, ať sedí s webem.
const fs = require('fs');
const os = require('os');
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) {
  ({ chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright'));
}

const ROOT = path.resolve(__dirname, '..');
const url = p => 'file://' + path.join(ROOT, p);
const ADOPTED = 396;

const PAW = '<svg viewBox="0 0 48 48" fill="currentColor"><ellipse cx="11" cy="20" rx="4.6" ry="6" transform="rotate(-18 11 20)"/><ellipse cx="19.5" cy="11.5" rx="4.8" ry="6.4" transform="rotate(-6 19.5 11.5)"/><ellipse cx="29.5" cy="11.5" rx="4.8" ry="6.4" transform="rotate(6 29.5 11.5)"/><ellipse cx="38" cy="20" rx="4.6" ry="6" transform="rotate(18 38 20)"/><path d="M24.5 22c-6.2 0-12.5 8.6-12.5 13.6 0 4 3.2 5.9 6.6 5.9 2.6 0 4-1.3 5.9-1.3s3.3 1.3 5.9 1.3c3.4 0 6.6-1.9 6.6-5.9C37 30.6 30.7 22 24.5 22z"/></svg>';

const OG = [
  { file: 'og-uvod.jpg', photos: ['assets/img/kocka-tuxedo.jpg'], eyebrow: 'Depozitum chlup-nechlup · Strakonice', title: 'Hledáme ten <em>pravý domov</em> pro opuštěné kočky.', foot: `${ADOPTED} koček už našlo domov · adopce bez poplatku` },
  { file: 'og-adopce.jpg', photos: ['assets/img/domov/ludvik-lucian.jpg'], eyebrow: 'Kočky k adopci · Strakonice', title: 'Najděte svou <em>spřízněnou duši</em>.', foot: 'Adopce bez poplatku · dospělé kočky kastrované' },
  { file: 'og-domov.jpg', photos: ['assets/img/domov/xia.jpg', 'assets/img/domov/bozanek.jpg', 'assets/img/domov/wilson.jpg'], eyebrow: 'Domov našli', title: `<em>${ADOPTED}</em> koček už má svého člověka.`, foot: 'Depozitum chlup-nechlup · Strakonice' },
  { file: 'og-docaska.jpg', photos: ['assets/img/eliot-a-emil.jpg'], eyebrow: 'Dočasná péče', title: 'Kočka doma <em>bez závazku</em> na celý život.', foot: 'Krmení, stelivo i veterinu platí depozitum' },
  { file: 'og-podpora.jpg', photos: ['assets/img/mourek.jpg'], eyebrow: 'Podpořte nás', title: 'Peníze jdou <em>na kočky</em>, ne na mzdy.', foot: 'Transparentní účet 6077760777/2010 · QR platba' },
  { file: 'og-nalez.jpg', photos: ['assets/img/odchyt.jpg'], eyebrow: 'Našli jste kočku?', title: 'Nejdřív volejte <em>obec</em>. Ze zákona.', foot: 'Postup krok za krokem · Depozitum chlup-nechlup' },
];

const css = `
  @font-face { font-family: Fraunces; src: url(${url('assets/fonts/fraunces-normal-latin.woff2')}) format('woff2'); font-weight: 500 700; unicode-range: U+0000-00FF; }
  @font-face { font-family: Fraunces; src: url(${url('assets/fonts/fraunces-normal-latin-ext.woff2')}) format('woff2'); font-weight: 500 700; unicode-range: U+0100-024F; }
  @font-face { font-family: Fraunces; font-style: italic; src: url(${url('assets/fonts/fraunces-italic-latin.woff2')}) format('woff2'); font-weight: 500 700; unicode-range: U+0000-00FF; }
  @font-face { font-family: Fraunces; font-style: italic; src: url(${url('assets/fonts/fraunces-italic-latin-ext.woff2')}) format('woff2'); font-weight: 500 700; unicode-range: U+0100-024F; }
  @font-face { font-family: Figtree; src: url(${url('assets/fonts/figtree-normal-latin.woff2')}) format('woff2'); font-weight: 400 800; unicode-range: U+0000-00FF; }
  @font-face { font-family: Figtree; src: url(${url('assets/fonts/figtree-normal-latin-ext.woff2')}) format('woff2'); font-weight: 400 800; unicode-range: U+0100-024F; }
  * { box-sizing: border-box; margin: 0; }
  body { width: 1200px; height: 630px; background: #f7f0e5; color: #2b211b; font-family: Figtree, sans-serif; display: grid; grid-template-columns: 1fr 500px; grid-template-rows: 630px; overflow: hidden; position: relative; }
  .blob { position: absolute; width: 760px; height: 760px; border-radius: 50%; right: -260px; top: -300px; background: radial-gradient(circle at 30% 30%, rgba(243,200,104,.75), transparent 70%); }
  .text { position: relative; padding: 64px 40px 56px 72px; display: flex; flex-direction: column; }
  .brand { display: flex; align-items: center; gap: 14px; font-family: Fraunces, serif; font-weight: 700; font-size: 30px; }
  .brand svg { width: 52px; height: 52px; color: #b94f1b; }
  .eyebrow { margin-top: auto; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; font-size: 20px; color: #9a3c14; }
  h1 { font-family: Fraunces, serif; font-weight: 600; font-size: 68px; line-height: 1.04; letter-spacing: -.02em; margin: 14px 0 26px; font-variation-settings: "SOFT" 100; }
  h1 em { color: #b94f1b; font-style: italic; }
  .foot { font-size: 24px; font-weight: 600; color: #5d4f45; }
  .photos { position: relative; height: 630px; min-height: 0; padding: 40px 48px 40px 0; display: grid; gap: 14px; }
  .photos img { min-height: 0; min-width: 0; }
  .photos.n3 { grid-template-rows: 1.3fr 1fr; grid-template-columns: 1fr 1fr; }
  .photos.n3 img:first-child { grid-column: 1 / -1; }
  .photos img { width: 100%; height: 100%; object-fit: cover; border-radius: 36px; box-shadow: 0 24px 50px -24px rgba(43,33,27,.5); }
`;

const ogHtml = o => `<!doctype html><html lang="cs"><head><meta charset="utf-8"><style>${css}</style></head><body>
  <div class="blob"></div>
  <div class="text">
    <div class="brand">${PAW}<span>chlup-nechlup</span></div>
    <div class="eyebrow">${o.eyebrow}</div>
    <h1>${o.title}</h1>
    <div class="foot">${o.foot}</div>
  </div>
  <div class="photos ${o.photos.length === 3 ? 'n3' : ''}">${o.photos.map(p => `<img src="${url(p)}">`).join('')}</div>
</body></html>`;

const iconHtml = (size, padding) => `<!doctype html><html><head><style>* { margin: 0 } body { width: ${size}px; height: ${size}px; background: #b94f1b; display: grid; place-items: center; }
  svg { width: ${size - padding * 2}px; height: ${size - padding * 2}px; color: #fffaf2; }</style></head><body>${PAW}</body></html>`;

(async () => {
  const outDir = path.join(ROOT, 'assets/img/og');
  fs.mkdirSync(outDir, { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'og-'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  for (const o of OG) {
    const f = path.join(tmp, o.file + '.html');
    fs.writeFileSync(f, ogHtml(o));
    await page.goto('file://' + f, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(outDir, o.file), type: 'jpeg', quality: 86 });
    console.log('assets/img/og/' + o.file);
  }
  for (const [name, size, pad] of [['apple-touch-icon.png', 180, 30], ['icon-192.png', 192, 32], ['icon-512.png', 512, 84]]) {
    const f = path.join(tmp, name + '.html');
    fs.writeFileSync(f, iconHtml(size, pad));
    await page.setViewportSize({ width: size, height: size });
    await page.goto('file://' + f);
    await page.screenshot({ path: path.join(ROOT, 'assets/img', name) });
    console.log('assets/img/' + name);
  }
  await browser.close();
  fs.rmSync(tmp, { recursive: true, force: true });
})();
