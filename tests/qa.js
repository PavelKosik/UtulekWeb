// Kompletní test webu: stránky, odkazy, interakce, přetékání na mobilu a přístupnost (axe-core).
// Spuštění:  npm test                     (spustí vlastní server nad složkou webu)
//            npm run test:live            (otestuje zveřejněný web)
//            node tests/qa.js <url> <výstupní složka>
const fs = require('fs');
const path = require('path');
const http = require('http');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) {
  ({ chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright'));
}

const ROOT = path.resolve(__dirname, '..');
const OUT = process.argv[3] || path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });
const PAGES = ['index.html', 'kocky-k-adopci.html', 'nasli-domov.html', 'docasna-pece.html', 'podporte-nas.html', 'nasli-jste-kocku.html', 'pro-obce.html', 'o-nas.html', 'plakat.html', 'soukromi.html'];
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36';
const AXE = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.xml': 'application/xml', '.txt': 'text/plain' };

function serve() {
  return new Promise(resolve => {
    const server = http.createServer((req, res) => {
      let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      if (p.endsWith('/')) p += 'index.html';
      const file = path.join(ROOT, p);
      if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end('not found'); }
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
      fs.createReadStream(file).pipe(res);
    });
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

let BASE = process.argv[2];

const report = { base: null, pages: {}, links: [], anchors: [], overflow: [], interactions: [], axe: {}, problems: [] };
const problem = (where, what) => { report.problems.push(`${where}: ${what}`); };

async function newCtx(browser, opts = {}) {
  const ctx = await browser.newContext({ locale: 'cs-CZ', userAgent: UA, ...opts });
  await ctx.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined }));
  return ctx;
}

async function scrollThrough(p) {
  await p.evaluate(async () => {
    const step = innerHeight * 0.8;
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) { scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 160)); }
    scrollTo({ top: 0, behavior: 'instant' });
  });
}

(async () => {
  let server = null;
  if (!BASE) { server = await serve(); BASE = `http://127.0.0.1:${server.address().port}/`; console.log('Testuji', BASE); }
  report.base = BASE;
  const browser = await chromium.launch({ channel: 'chromium', args: ['--disable-blink-features=AutomationControlled'] });

  // 1) Načtení stránek, chyby, velikost, základní SEO/HTML kontroly
  const internalLinks = new Set();
  for (const pg of PAGES) {
    const ctx = await newCtx(browser, { viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    const info = { console: [], failed: [], bytes: 0, requests: 0, thirdParty: new Set() };
    const ours = u => u.startsWith(BASE) || /pesweb\.cz\/widget/.test(u);
    // chyby z cizích skriptů uvnitř widgetu (reklamy, analytika Peswebu) nejsou chyby webu
    p.on('console', m => { const at = m.location().url || ''; if ((m.type() === 'error' || m.type() === 'warning') && (!at || ours(at))) info.console.push(`${m.type()}: ${m.text().slice(0, 200)} ${at}`); });
    p.on('pageerror', e => info.console.push('pageerror: ' + e.message));
    p.on('requestfailed', r => { if (ours(r.url())) info.failed.push(`${r.failure()?.errorText} ${r.url()}`); });
    p.on('response', async r => {
      info.requests++;
      const u = new URL(r.url());
      if (!r.url().startsWith(BASE)) info.thirdParty.add(u.host);
      if (r.status() >= 400 && ours(r.url())) info.failed.push(`HTTP ${r.status()} ${r.url()}`);
      if (r.url().startsWith(BASE)) { try { const b = await r.body(); info.bytes += b.length; } catch (e) {} }
    });
    const t0 = Date.now();
    await p.goto(BASE + pg, { waitUntil: 'networkidle', timeout: 60000 });
    info.loadMs = Date.now() - t0;
    await scrollThrough(p);
    await p.waitForTimeout(2500);
    const dom = await p.evaluate(() => {
      const abs = h => { try { return new URL(h, location.href).href; } catch (e) { return h; } };
      const imgs = [...document.images];
      return {
        title: document.title,
        titleLen: document.title.length,
        desc: document.querySelector('meta[name=description]')?.content || '',
        canonical: document.querySelector('link[rel=canonical]')?.href || '',
        ogImage: document.querySelector('meta[property="og:image"]')?.content || '',
        h1: document.querySelectorAll('h1').length,
        headings: [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => +h.tagName[1]),
        imgNoAlt: imgs.filter(i => !i.hasAttribute('alt')).map(i => i.src),
        imgNoDims: imgs.filter(i => !i.getAttribute('width') && !i.closest('.journey__media, .marquee, .collage, .poster')).map(i => i.src.split('/').pop()),
        imgBroken: imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => i.src),
        imgOversized: imgs.filter(i => i.naturalWidth > 0 && i.getBoundingClientRect().width > 0 && i.naturalWidth > i.getBoundingClientRect().width * 2.6).map(i => `${i.src.split('/').pop()} ${i.naturalWidth}px→${Math.round(i.getBoundingClientRect().width)}px`),
        links: [...document.querySelectorAll('a[href]')].map(a => ({ href: a.getAttribute('href'), abs: abs(a.getAttribute('href')), text: (a.textContent || a.getAttribute('aria-label') || '').trim(), blank: a.target === '_blank', rel: a.rel })),
        ids: [...document.querySelectorAll('[id]')].map(e => e.id),
        dupIds: (() => { const c = {}; document.querySelectorAll('[id]').forEach(e => c[e.id] = (c[e.id] || 0) + 1); return Object.keys(c).filter(k => c[k] > 1); })(),
        buttonsNoName: [...document.querySelectorAll('button')].filter(b => !(b.innerText.trim() || b.getAttribute('aria-label'))).length,
        iframes: [...document.querySelectorAll('iframe')].map(f => ({ src: f.src.slice(0, 80), h: f.offsetHeight })),
        revealHidden: [...document.querySelectorAll('.reveal')].filter(e => getComputedStyle(e).opacity === '0').length,
      };
    });
    info.thirdPartyList = [...info.thirdParty];
    info.dom = { ...dom, links: undefined, ids: undefined };
    report.pages[pg] = info;
    if (info.console.length) problem(pg, 'console: ' + info.console.join(' | '));
    if (info.failed.length) problem(pg, 'failed: ' + info.failed.join(' | '));
    if (dom.h1 !== 1) problem(pg, `h1 count ${dom.h1}`);
    for (let i = 1; i < dom.headings.length; i++) if (dom.headings[i] > dom.headings[i - 1] + 1) { problem(pg, `heading skip h${dom.headings[i - 1]}→h${dom.headings[i]}`); break; }
    if (dom.imgNoAlt.length) problem(pg, 'img without alt: ' + dom.imgNoAlt.join(', '));
    if (dom.imgBroken.length) problem(pg, 'broken img: ' + dom.imgBroken.join(', '));
    if (dom.dupIds.length) problem(pg, 'duplicate ids: ' + dom.dupIds.join(', '));
    if (dom.buttonsNoName) problem(pg, `${dom.buttonsNoName} buttons without name`);
    if (dom.revealHidden) problem(pg, `${dom.revealHidden} .reveal still hidden after scroll`);
    if (!dom.canonical) problem(pg, 'no canonical');
    if (!/^https?:/.test(dom.ogImage)) problem(pg, `og:image not absolute (${dom.ogImage})`);
    if (dom.titleLen > 65) problem(pg, `title long (${dom.titleLen})`);
    if (dom.desc.length < 70 || dom.desc.length > 165) problem(pg, `description length ${dom.desc.length}`);
    for (const l of dom.links) {
      if (!l.text) problem(pg, `link without text: ${l.href}`);
      if (l.blank && !/noopener/.test(l.rel)) problem(pg, `target=_blank without noopener: ${l.href}`);
      if (l.abs.startsWith(BASE)) internalLinks.add(l.abs);
    }
    report.pages[pg].allIds = dom.ids;
    await p.screenshot({ path: path.join(OUT, `full-${pg}.png`), fullPage: true });
    await ctx.close();
  }

  // 2) Interní odkazy a kotvy
  const ctxL = await newCtx(browser);
  const pl = await ctxL.newPage();
  for (const link of internalLinks) {
    const [noHash, hash] = link.split('#');
    const res = await pl.request.get(noHash).catch(() => null);
    const st = res ? res.status() : 'ERR';
    report.links.push(`${st} ${link}`);
    if (st !== 200) problem('links', `${st} ${link}`);
    if (hash) {
      const pg = noHash.replace(BASE, '').split('?')[0] || 'index.html';
      const ids = report.pages[pg]?.allIds || [];
      if (!ids.includes(decodeURIComponent(hash))) problem('anchors', `#${hash} missing on ${pg}`);
    }
  }
  await ctxL.close();
  for (const pg of PAGES) delete report.pages[pg].allIds;

  // 3) Přetékání do strany na různých šířkách
  for (const w of [320, 360, 390, 768, 1024, 1920]) {
    const ctx = await newCtx(browser, { viewport: { width: w, height: 800 } });
    const p = await ctx.newPage();
    for (const pg of PAGES) {
      await p.goto(BASE + pg, { waitUntil: 'networkidle', timeout: 60000 });
      await scrollThrough(p);
      const off = await p.evaluate(() => {
        const vw = document.documentElement.clientWidth;
        const clips = el => { for (let a = el.parentElement; a; a = a.parentElement) { const o = getComputedStyle(a); if (/(hidden|clip)/.test(o.overflowX) && a !== document.body) return true; } return false; };
        return [...document.querySelectorAll('body *')].filter(e => {
          const r = e.getBoundingClientRect();
          if (!r.width || !r.height) return false;
          if (getComputedStyle(e).position === 'fixed') return false;
          return (r.right > vw + 1 || r.left < -1) && !clips(e);
        }).slice(0, 5).map(e => `${e.tagName.toLowerCase()}.${[...e.classList].join('.')} right=${Math.round(e.getBoundingClientRect().right)} vw=${vw}`);
      });
      if (off.length) { report.overflow.push(`${w}px ${pg}: ${off.join('; ')}`); problem('overflow', `${w}px ${pg}: ${off[0]}`); }
    }
    await ctx.close();
  }

  // 4) Interakce
  const check = (name, ok, detail = '') => { report.interactions.push(`${ok ? 'PASS' : 'FAIL'} ${name}${detail ? ' — ' + detail : ''}`); if (!ok) problem('interaction', `${name} ${detail}`); };
  {
    const ctx = await newCtx(browser, { viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
    await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: new URL(BASE).origin });
    const p = await ctx.newPage();
    await p.goto(BASE + 'index.html', { waitUntil: 'networkidle' });
    await p.click('.nav-toggle');
    await p.waitForTimeout(400);
    check('mobile menu opens', await p.evaluate(() => document.body.classList.contains('nav-open') && getComputedStyle(document.querySelector('.nav')).visibility === 'visible'));
    check('menu toggle aria-expanded', (await p.getAttribute('.nav-toggle', 'aria-expanded')) === 'true');
    await p.keyboard.press('Escape');
    await p.waitForTimeout(400);
    check('Escape closes menu', await p.evaluate(() => !document.body.classList.contains('nav-open')));
    await p.click('.nav-toggle'); await p.waitForTimeout(300);
    await p.click('.nav a[href="o-nas.html"]'); await p.waitForURL(/o-nas/);
    check('menu link navigates', p.url().endsWith('o-nas.html'));
    await p.goto(BASE + 'index.html', { waitUntil: 'networkidle' });
    check('mobile CTA hidden on hero', await p.evaluate(() => !document.querySelector('.mobile-cta').classList.contains('is-visible')));
    await p.evaluate(() => scrollTo({ top: document.querySelector('#pribeh').offsetTop, behavior: 'instant' })); await p.waitForTimeout(600);
    check('mobile CTA visible after hero', await p.evaluate(() => document.querySelector('.mobile-cta').classList.contains('is-visible') && getComputedStyle(document.querySelector('.mobile-cta')).visibility === 'visible'));
    await p.evaluate(() => document.querySelector('#dar').scrollIntoView({ behavior: 'instant' })); await p.waitForTimeout(600);
    check('mobile CTA hidden in donate section', await p.evaluate(() => !document.querySelector('.mobile-cta').classList.contains('is-visible')));
    check('mobile payment hint visible', await p.evaluate(() => getComputedStyle(document.querySelector('#dar .mobile-hint')).display !== 'none'));
    await p.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' })); await p.waitForTimeout(600);
    check('mobile CTA hidden at footer', await p.evaluate(() => !document.querySelector('.mobile-cta').classList.contains('is-visible')));
    await p.goto(BASE + 'kocky-k-adopci.html', { waitUntil: 'networkidle' });
    check('mobile CTA on adoption page opens questionnaire', await p.evaluate(() => document.querySelector('.mobile-cta a').getAttribute('href') === '#dotaznik' && !!document.querySelector('#dotaznik')));
    await ctx.close();
  }
  {
    const ctx = await newCtx(browser, { viewport: { width: 1440, height: 900 } });
    await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: new URL(BASE).origin });
    const p = await ctx.newPage();
    await p.goto(BASE + 'index.html', { waitUntil: 'networkidle' });
    // skip link
    await p.keyboard.press('Tab');
    check('skip link first in tab order', await p.evaluate(() => document.activeElement.classList.contains('skip-link')));
    // tabs + lazy widget
    await p.evaluate(() => document.querySelector('#kocky').scrollIntoView());
    await p.waitForTimeout(5000);
    check('first widget iframe loaded', await p.evaluate(() => !!document.querySelector('#panel-cekaji iframe')));
    const h1 = await p.evaluate(() => document.querySelector('#panel-cekaji iframe')?.offsetHeight || 0);
    check('widget auto-height', h1 > 650, `${h1}px`);
    await p.click('#tab-nove');
    await p.waitForTimeout(5000);
    check('tab switch shows second panel', await p.evaluate(() => !document.querySelector('#panel-nove').hidden && document.querySelector('#panel-cekaji').hidden));
    check('second widget lazy-loaded on tab click', await p.evaluate(() => !!document.querySelector('#panel-nove iframe')));
    await p.focus('#tab-nove'); await p.keyboard.press('ArrowLeft');
    check('arrow key switches tab', await p.evaluate(() => document.querySelector('#tab-cekaji').getAttribute('aria-selected') === 'true' && document.activeElement.id === 'tab-cekaji'));
    // amounts
    await p.evaluate(() => document.querySelector('#dar').scrollIntoView());
    await p.waitForTimeout(800);
    await p.click('#dar [data-amount="300"]');
    const st = await p.evaluate(() => ({ src: document.querySelector('#dar .account__qr img').getAttribute('src'), impact: document.querySelector('#dar .impact').textContent, pressed: document.querySelector('#dar [data-amount="300"]').getAttribute('aria-pressed'), cap: document.querySelector('#dar .account__qr span').textContent }));
    check('amount 300 switches QR', st.src.endsWith('qr-platba-300.svg') && st.pressed === 'true' && /300/.test(st.impact) && /300/.test(st.cap), JSON.stringify(st));
    await p.click('#dar [data-amount=""]');
    check('amount "Jiná" uses QR without amount', (await p.getAttribute('#dar .account__qr img', 'src')).endsWith('qr-platba.svg'));
    await p.click('#dar [data-amount="1500"]');
    const sv = await p.evaluate(() => ({ href: document.querySelector('#dar .qr-save').getAttribute('href'), dl: document.querySelector('#dar .qr-save').getAttribute('download') }));
    check('QR save link follows amount', sv.href.endsWith('qr-platba-1500.png') && sv.dl === 'qr-platba-depozitum-1500.png', JSON.stringify(sv));
    const png = await p.request.get(new URL(sv.href, BASE).href);
    check('QR PNG downloadable', png.status() === 200 && (png.headers()['content-type'] || '').includes('png'));
    // copy
    await p.click('#dar .account [data-copy]');
    const clip = await p.evaluate(() => navigator.clipboard.readText()).catch(e => 'ERR ' + e.message);
    check('copy account number', clip === '6077760777/2010', clip);
    // counters
    await p.evaluate(() => document.querySelector('.stats').scrollIntoView({ block: 'center' }));
    await p.waitForTimeout(2600);
    const nums = await p.evaluate(() => [...document.querySelectorAll('.stats .stat__num')].map(e => e.textContent));
    check('counters reach final values', nums[0] === '396' && nums[1] === '65', nums.join(' / '));
    // journey
    const steps = await p.evaluate(async () => {
      const out = [];
      for (const s of document.querySelectorAll('.journey__step')) {
        s.scrollIntoView({ block: 'center' });
        await new Promise(r => setTimeout(r, 450));
        out.push(document.querySelector('.journey__label').textContent);
      }
      return out;
    });
    check('journey label follows steps', steps.join('|') === 'Odchyt|Karanténa a léčba|Kastrace|Dočasná péče|Nový domov', steps.join('|'));
    // header hide/show
    await p.evaluate(() => scrollTo({ top: 2000, behavior: 'instant' })); await p.waitForTimeout(200); await p.evaluate(() => scrollTo({ top: 2600, behavior: 'instant' })); await p.waitForTimeout(400);
    const hidden = await p.evaluate(() => document.querySelector('.site-header').classList.contains('is-hidden'));
    await p.evaluate(() => scrollTo({ top: 2300, behavior: 'instant' })); await p.waitForTimeout(400);
    const shown = await p.evaluate(() => !document.querySelector('.site-header').classList.contains('is-hidden'));
    check('header hides on scroll down, shows on scroll up', hidden && shown);
    await ctx.close();
  }
  {
    const ctx = await newCtx(browser, { viewport: { width: 1280, height: 900 } });
    const p = await ctx.newPage();
    await p.goto(BASE + 'docasna-pece.html', { waitUntil: 'networkidle' });
    const share = await p.evaluate(() => ({ fb: document.querySelector('[data-share-fb]').href, wa: document.querySelector('[data-share-wa]').href, copy: document.querySelector('[data-share-copy]').getAttribute('data-copy') }));
    check('share links point to page', share.fb.includes(encodeURIComponent(BASE + 'docasna-pece.html')) && share.wa.includes(encodeURIComponent(BASE + 'docasna-pece.html')) && share.copy === BASE + 'docasna-pece.html', JSON.stringify(share));
    await p.goto(BASE + 'podporte-nas.html', { waitUntil: 'networkidle' });
    const sh2 = await p.evaluate(() => document.querySelector('#sdileni [data-share-copy]').getAttribute('data-copy'));
    check('share on support page points to homepage', sh2 === BASE + 'index.html', sh2);
    await p.evaluate(() => document.querySelector('.bars').scrollIntoView({ block: 'center' })); await p.waitForTimeout(1500);
    await p.hover('.bars__row:nth-child(2)'); await p.waitForTimeout(300);
    check('chart tooltip on hover', await p.evaluate(() => getComputedStyle(document.querySelector('.bars__row:nth-child(2) .bars__tip')).opacity === '1'));
    await ctx.close();
  }
  {
    // filtry na stránce Kočky k adopci (věk, pohlaví, řazení) a přímé odkazy
    const ctx = await newCtx(browser, { viewport: { width: 1280, height: 900 } });
    const p = await ctx.newPage();
    await p.goto(BASE + 'kocky-k-adopci.html?vek=seniori', { waitUntil: 'networkidle' });
    await p.waitForTimeout(5000);
    const src = await p.evaluate(() => document.querySelector('[data-pesweb] iframe')?.src || '');
    const checked = await p.evaluate(() => document.querySelector('input[name=vek]:checked').value);
    check('adoption filter deep link (?vek=seniori)', /age=8y/.test(src) && checked === 'seniori', checked);
    await p.getByText('Kocouři', { exact: true }).click();
    await p.waitForTimeout(5000);
    const src2 = await p.evaluate(() => document.querySelector('[data-pesweb] iframe')?.src || '');
    check('filter change reloads widget and updates URL', /sex=kocour/.test(src2) && /age=8y/.test(src2) && /pohlavi=kocour/.test(p.url()), p.url().split('/').pop());
    const st = await p.evaluate(() => ({ h: document.querySelector('[data-pesweb] iframe').offsetHeight, hint: !document.querySelector('[data-filter-empty]').hidden }));
    check('empty-result hint matches widget state', (st.h <= 410) === st.hint, JSON.stringify(st));
    await p.getByText('Všechny', { exact: true }).click();
    await p.getByText('Kočky i kocouři', { exact: true }).click();
    await p.waitForTimeout(1500);
    check('resetting filters clears URL', !p.url().includes('?'), p.url().split('/').pop());
    await ctx.close();
  }
  {
    // dotazníky: předvyplnění, povinná pole, složení zprávy
    const ctx = await newCtx(browser, { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: new URL(BASE).origin });
    const p = await ctx.newPage();
    await p.goto(BASE + 'kocky-k-adopci.html?kocka=Zina#dotaznik', { waitUntil: 'load' });
    const f = p.locator('#dotaznik');
    check('questionnaire prefills cat from URL', (await f.locator('[name=kocka]').inputValue()) === 'Zina');
    await f.locator('[data-qform-copy]').click();
    check('questionnaire asks for contact and conditions', await f.locator('[data-qform-error]').isVisible());
    check('children age field hidden until "Děti" is ticked', !(await f.locator('[name=vek_deti]').isVisible()));
    await f.getByText('V bytě', { exact: true }).click();
    await f.getByText('Děti', { exact: true }).click();
    check('children age field appears', await f.locator('[name=vek_deti]').isVisible());
    await f.locator('[name=vek_deti]').fill('5 let');
    await f.locator('[name=jmeno]').fill('Test');
    await f.locator('[name=telefon]').fill('777 000 000');
    await f.locator('[name=podminky]').check();
    check('questionnaire error clears once fields are filled', !(await f.locator('[data-qform-error]').isVisible()));
    await f.locator('[data-qform-copy]').click();
    const msg = await p.evaluate(() => navigator.clipboard.readText()).catch(() => '');
    check('questionnaire composes message', /Zina/.test(msg) && /v bytě/.test(msg) && /děti \(5 let\)/.test(msg) && /Tel\.: 777 000 000/.test(msg) && !(await f.locator('[data-qform-error]').isVisible()), msg.split('\n').slice(0, 2).join(' / '));
    check('SMS option on touch devices', await f.locator('[data-qform-sms]').isVisible());
    await f.locator('[data-qform-mail]').click().catch(() => {});
    await p.waitForTimeout(1200);
    check('after sending: fallback with the e-mail address', await f.locator('[data-qform-after]').isVisible() && /@/.test(await f.locator('[data-qform-after]').innerText()));
    await p.goto(BASE + 'docasna-pece.html#prihlaska', { waitUntil: 'load' });
    const g = p.locator('#prihlaska');
    await g.getByText('Kočku', { exact: true }).click();
    await g.getByText('Nemám', { exact: true }).click();
    check('foster form: "Nemám" clears other animals', !(await g.locator('[name=zvirata][value="kočku"]').isChecked()) && /žádná zvířata/.test(await g.locator('[data-qform-preview]').innerText()));
    await ctx.close();
  }
  for (const [w, h, mobile] of [[1280, 800, false], [390, 844, true]]) {
    // dlouhý seznam: patička Peswebu („Načíst další“) je vypnutá, další kočky odkrývá tlačítko webu
    const ctx = await newCtx(browser, { viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile });
    const p = await ctx.newPage();
    await p.goto(BASE + 'kocky-k-adopci.html', { waitUntil: 'load' });
    await p.locator('[data-widget-clip]').scrollIntoViewIfNeeded();
    const clipped = await p.waitForFunction(() => document.querySelector('[data-widget-clip]').classList.contains('is-clipped'), null, { timeout: 30000 }).then(() => true, () => false);
    const footer = async () => { const f = p.frames().find(fr => /pesweb\.cz\/widget/.test(fr.url())); return f ? f.evaluate(() => /Zobrazeno|Načíst další/.test(document.body.innerText)).catch(() => null) : null; };
    const btn = p.locator('[data-widget-more] button');
    const own = await footer();
    check(`cat list (${w}px): Pesweb footer off, own button shown`, clipped && own === false && await btn.isVisible(), JSON.stringify({ clipped, footer: own }));
    let clicks = 0;
    while (clicks < 40 && await btn.isVisible()) { await btn.click(); clicks++; await p.waitForTimeout(150); }
    await p.waitForTimeout(900);
    const end = await p.evaluate(() => { const c = document.querySelector('[data-widget-clip]'); return { clip: c.offsetHeight, frame: c.querySelector('iframe').offsetHeight }; });
    check(`cat list (${w}px): button reveals every cat, then hides`, clicks > 0 && !(await btn.isVisible()) && Math.abs(end.clip - end.frame) <= 2, JSON.stringify({ clicks, ...end }));
    await p.goto(BASE + 'index.html', { waitUntil: 'load' });
    await p.locator('#kocky [data-pesweb]').first().scrollIntoViewIfNeeded();
    await p.waitForFunction(() => { const fr = document.querySelector('#kocky [data-pesweb] iframe'); return fr && fr.offsetHeight !== 600; }, null, { timeout: 30000 }).catch(() => {});
    const home = await footer();
    check(`homepage cats (${w}px): no Pesweb footer`, home === false, String(home));
    await ctx.close();
  }
  for (const [w, h, mobile] of [[1280, 800, false], [390, 844, true]]) {
    // odkaz „Mám zájem“: widget nad dotazníkem po načtení naroste, dotazník ale musí zůstat na očích
    const ctx = await newCtx(browser, { viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile });
    const p = await ctx.newPage();
    await p.goto(BASE + 'kocky-k-adopci.html?kocka=Celesta#dotaznik', { waitUntil: 'load' });
    await p.waitForFunction(() => { const fr = document.querySelector('[data-pesweb] iframe'); return fr && fr.offsetHeight > 500; }, null, { timeout: 20000 }).catch(() => {});
    await p.waitForTimeout(1500);
    const top = await p.evaluate(() => Math.round(document.querySelector('#dotaznik').getBoundingClientRect().top));
    check(`deep link #dotaznik stays in view after the widget loads (${w}px)`, top > -20 && top < h * 0.5, 'top ' + top);
    await ctx.close();
  }
  {
    const ctx = await newCtx(browser, { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const p = await ctx.newPage();
    const cta = async pg => { await p.goto(BASE + pg, { waitUntil: 'load' }); return p.evaluate(() => [...document.querySelectorAll('.mobile-cta a')].map(a => a.getAttribute('href'))); };
    check('mobile bar: foster page leads to the sign-up form', (await cta('docasna-pece.html'))[0] === '#prihlaska');
    check('mobile bar: finder page calls 156', (await cta('nasli-jste-kocku.html'))[0] === 'tel:156');
    check('mobile bar: none on the donation page', (await cta('podporte-nas.html')).length === 0);
    await ctx.close();
  }
  {
    const ctx = await newCtx(browser, { viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
    const p = await ctx.newPage();
    await p.goto(BASE + 'index.html', { waitUntil: 'networkidle' });
    await p.waitForTimeout(500);
    const r = await p.evaluate(() => ({ hidden: [...document.querySelectorAll('.reveal')].filter(e => getComputedStyle(e).opacity !== '1').length, words: [...document.querySelectorAll('.statement .w')].filter(w => !w.classList.contains('is-lit')).length }));
    check('reduced motion: everything visible without scrolling', r.hidden === 0 && r.words === 0, JSON.stringify(r));
    await ctx.close();
  }
  {
    const ctx = await newCtx(browser, { viewport: { width: 1280, height: 900 }, javaScriptEnabled: false });
    const p = await ctx.newPage();
    await p.goto(BASE + 'index.html', { waitUntil: 'load' });
    const r = await p.evaluate(() => ({ hidden: [...document.querySelectorAll('.reveal')].filter(e => getComputedStyle(e).opacity !== '1').length, fallback: !!document.querySelector('.widget-fallback a') }));
    check('no-JS: content visible, Pesweb fallback link', r.hidden === 0 && r.fallback, JSON.stringify(r));
    await ctx.close();
  }

  // 5) web je vždy světlý, i když má systém tmavý režim
  {
    const ctx = await newCtx(browser, { viewport: { width: 1280, height: 900 }, colorScheme: 'dark' });
    const p = await ctx.newPage();
    await p.goto(BASE + 'index.html', { waitUntil: 'load' });
    const bg = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
    check('dark system theme: page stays light', bg === 'rgb(247, 240, 229)', bg);
    await ctx.close();
  }

  // 6) úvod: tlačítka vidět bez scrollování, na vysokých monitorech bez obří mezery
  for (const [w, h] of [[1280, 720], [1366, 768], [1440, 900], [1920, 1080], [1363, 1472], [2560, 1440], [390, 844]]) {
    const ctx = await newCtx(browser, { viewport: { width: w, height: h }, reducedMotion: 'reduce' });
    const p = await ctx.newPage();
    await p.goto(BASE + 'index.html', { waitUntil: 'load' });
    const m = await p.evaluate(() => {
      const b = s => document.querySelector(s).getBoundingClientRect();
      return { cta: Math.round(b('.hero .btn-row').bottom), gap: Math.round(b('.hero .wrap').top - b('.site-header').bottom) };
    });
    const ok = m.cta <= h && (w <= 860 || m.gap <= 200);
    check(`hero ${w}×${h}: buttons above the fold, no huge gap`, ok, JSON.stringify(m));
    await ctx.close();
  }

  // 7) velký monitor (2560 px): web se úměrně zvětší (1rem = 1vw) a vyplní šířku, nic nepřetéká
  {
    const ctx = await newCtx(browser, { viewport: { width: 2560, height: 1430 }, reducedMotion: 'reduce' });
    const p = await ctx.newPage();
    await p.goto(BASE + 'index.html', { waitUntil: 'load' });
    const m = await p.evaluate(() => ({ root: getComputedStyle(document.documentElement).fontSize, wrap: Math.round(document.querySelector('.hero .wrap').getBoundingClientRect().width), overflow: document.documentElement.scrollWidth - innerWidth, cue: getComputedStyle(document.querySelector('.scroll-cue')).display }));
    check('2560×1430: page scales up to fill the screen', m.root === '25.6px' && m.wrap > 2560 * 0.65 && m.overflow <= 0 && m.cue === 'none', JSON.stringify(m));
    await ctx.close();
  }

  // 8) axe-core
  for (const scheme of ['light']) {
    for (const pg of PAGES) {
      const ctx = await newCtx(browser, { viewport: { width: 1280, height: 900 }, colorScheme: scheme, reducedMotion: 'reduce' });
      const p = await ctx.newPage();
      await p.goto(BASE + pg, { waitUntil: 'networkidle', timeout: 60000 });
      await p.waitForTimeout(800);
      await p.addScriptTag({ content: AXE });
      const res = await p.evaluate(async () => {
        const r = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] }, iframes: false });
        return r.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' ') + (n.any[0]?.data?.contrastRatio ? ` (${n.any[0].data.contrastRatio}:1 ${n.any[0].data.fgColor} on ${n.any[0].data.bgColor})` : '')) }));
      });
      report.axe[`${scheme} ${pg}`] = res;
      for (const v of res) problem(`axe ${scheme} ${pg}`, `${v.impact} ${v.id} ×${v.n}: ${v.sample.join(' | ')}`);
      await ctx.close();
    }
  }

  await browser.close();
  if (server) server.close();
  for (const i of Object.values(report.pages)) delete i.thirdParty;
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 1));
  console.log('=== PAGES');
  for (const [pg, i] of Object.entries(report.pages)) console.log(`${pg.padEnd(24)} ${String(Math.round(i.bytes / 1024)).padStart(5)} kB own, ${i.requests} req, ${i.loadMs} ms, 3rd: ${i.thirdPartyList.join(',')} | oversized: ${i.dom.imgOversized.join('; ')} | noDims: ${i.dom.imgNoDims.length}`);
  console.log('=== INTERACTIONS'); console.log(report.interactions.join('\n'));
  console.log(`=== PROBLEMS (${report.problems.length})`); console.log(report.problems.join('\n'));
  process.exitCode = report.problems.length ? 1 : 0;
})().catch(e => { console.error('QA crashed:', e); process.exit(1); });
