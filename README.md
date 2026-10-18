# Depozitum chlup-nechlup — nový web

Nový web pro [Depozitum chlup-nechlup](https://www.facebook.com/depozitumchlupnechlup), domácí depozitum pro odchyt, léčbu a kastraci koček ze Strakonic a okolí.

Je to čistě statický web: HTML, CSS a trocha JavaScriptu, bez knihoven a bez build kroku. Dá se nahrát na jakýkoli hosting (GitHub Pages, Netlify, Cloudflare Pages, Wedos…).

## Stránky

| Soubor | Obsah |
| --- | --- |
| `index.html` | Úvod: výzva (akutní adopce), živé kočky „Čekají nejdéle / Nově v depozitu“, čísla, cesta kočky (scrollovací), jak pomoct, dar s QR platbou a trvalým příkazem, galerie „Domov našli“, nález kočky, kontakt |
| `kocky-k-adopci.html` | Postup adopce ve 4 krocích, všechny kočky (widget Pesweb.cz), e-mail s otázkami, jak hledáme správný domov, první dny doma |
| `nasli-domov.html` | Počet a galerie koček, které našly domov, nejnovější adopce (widget Pesweb.cz) |
| `docasna-pece.html` | Dočasná péče, nejčastější obavy (FAQ), sdílení pro známé |
| `podporte-nas.html` | QR platba s volbou částky, trvalý příkaz, kam jdou peníze, potvrzení o daru, věcné dary, sdílení a plakát |
| `nasli-jste-kocku.html` | Postup při nálezu kočky (text Evy Hulcové), koťata, kastrace koček na dvoře, ztracená kočka |
| `o-nas.html` | Příběh depozita, Dita Uhriková, údaje o spolku |
| `plakat.html` | Plakát A4 k vytištění s QR kódem na kočky na Peswebu |
| `soukromi.html` | Soukromí a cookies |

Tipy pro psaní inzerátů na Pesweb jsou v `docs/tipy-pro-inzeraty.md`.

## Kočky k adopci

Seznam koček se načítá automaticky z portálu [Pesweb.cz](https://www.pesweb.cz/cz/depozitum-chlup-nechlup) přes jejich oficiální widget. **Když Dita přidá nebo upraví kočku na Peswebu, změní se i na webu.** Na web se kvůli kočkám nemusí sahat.

Widget se načte, až když k němu návštěvník doscrolluje (`assets/js/main.js`). Řazení „Čekají nejdéle“ používá `sort: foundDate:asc`, „Nově v depozitu“ `sort: createdAt:desc`.

Ručně se v `tools/build.py` aktualizují jen:
- `ADOPTED`, `LISTED`, `STATS_DATE`: počty z Peswebu,
- `APPEAL`: kočka s akutní adopcí na úvodní stránce (`None` = skrýt),
- `AMOUNTS`, `SPENDING`, `WISHLIST`: částky pro QR platbu, výdaje a co se hodí.

## Úpravy textů

Hlavička, patička i všechny stránky se generují ze souboru `tools/build.py`. Kontakty, číslo účtu a odkazy jsou nahoře v souboru. Po úpravě spusťte:

```sh
python3 tools/build.py
```

HTML soubory jdou upravovat i přímo, ale při dalším spuštění skriptu se přepíšou.

QR kódy pro platbu s částkou (`assets/img/qr-platba-*.svg`) se přegenerují, jen když je nainstalovaný balíček `qrcode` (`pip install qrcode`).

## Fotky a náhledy pro sdílení

- `python3 tools/optimize_images.py` vytvoří k fotkám zmenšené WebP verze (400 a 800 px). `tools/build.py` je sám použije v `<picture>`, starší prohlížeče dostanou JPG. Spusťte po přidání nebo výměně fotky (potřebuje Pillow).
- `node tools/og_images.js` vygeneruje náhledové obrázky pro sdílení na Facebooku a WhatsAppu (`assets/img/og/`, 1200×630) a ikony webu. Potřebuje Playwright.

## Testování

```sh
npm install
npx playwright install chromium
npm test            # otestuje web ve složce (spustí si vlastní server)
npm run test:live   # otestuje zveřejněný web
```

Test projde všech 9 stránek a zkontroluje:
- chyby v konzoli a nenačtené soubory,
- interní odkazy a kotvy,
- přetékání do strany na šířkách 320 až 1920 px,
- interakce: mobilní menu, záložky, volbu částky a QR, kopírování, sdílení, počítadla, „Cestu kočky“, mobilní lištu,
- režim bez animací a bez JavaScriptu,
- úvod na obrazovkách od 720 do 1472 px výšky: tlačítka vidět bez scrollování, žádná obří mezera,
- že web zůstane světlý i při tmavém režimu v systému,
- přístupnost (axe-core).

Celoplošné screenshoty a `report.json` uloží do `tests/out/`. Když najde problém, skončí s chybou.

## Spuštění lokálně

```sh
python3 -m http.server 8000
# a otevřít http://localhost:8000
```

Widget Pesweb se na `localhost` načte jen s nastaveným `baseUrl`, což skript dělá.

## Nasazení na GitHub Pages

Web běží na **https://pavelkosik.github.io/UtulekWeb/** a publikuje se z větve `gh-pages` (Settings → Pages → *Deploy from a branch* → `gh-pages`, `/ (root)`). Soubor `.nojekyll` už v repozitáři je.

Novou verzi zveřejníte tak, že ji pushnete do `gh-pages`, například:

```sh
git push origin HEAD:gh-pages
```

Po pár desítkách vteřin se změna objeví na webu.

## Fotky

Fotky v `assets/img/` jsou převzaté z původního webu depozita (webnode), fotky v `assets/img/domov/` a `celesta.jpg` z inzerátů depozita na Pesweb.cz. Všechny jsou zmenšené pro web.

Písma Fraunces a Figtree (SIL Open Font License) jsou v `assets/fonts/`, aby web nenačítal nic z Google Fonts.

QR platby (`assets/img/qr-platba*.svg`) jsou ve formátu SPD (QR Platba) na účet 6077760777/2010.
