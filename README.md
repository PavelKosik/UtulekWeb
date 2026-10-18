# Depozitum chlup-nechlup — nový web

Nový web pro [Depozitum chlup-nechlup](https://www.facebook.com/depozitumchlupnechlup), domácí depozitum pro odchyt, léčbu a kastraci koček ze Strakonic a okolí.

Je to čistě statický web: HTML, CSS a trocha JavaScriptu, bez knihoven a bez build kroku. Dá se nahrát na jakýkoli hosting (GitHub Pages, Netlify, Cloudflare Pages, Wedos…).

## Stránky

| Soubor | Obsah |
| --- | --- |
| `index.html` | Úvod: příběh, cesta kočky (scrollovací), živý výběr koček k adopci, jak pomoct, transparentní účet s QR platbou, co dělat při nálezu kočky, kontakt |
| `kocky-k-adopci.html` | Všechny kočky k adopci (widget Pesweb.cz), podmínky adopce, důvody zamítnutí |
| `nasli-domov.html` | Kočky, které už našly domov (widget Pesweb.cz) |
| `docasna-pece.html` | Jak funguje domácí depozitum / dočasná péče |
| `podporte-nas.html` | Transparentní účet, QR platba a další způsoby podpory |
| `nasli-jste-kocku.html` | Postup při nálezu kočky (text Evy Hulcové) |
| `o-nas.html` | Příběh depozita a Dity Uhrikové |

## Kočky k adopci

Seznam koček se načítá automaticky z portálu [Pesweb.cz](https://www.pesweb.cz/cz/depozitum-chlup-nechlup) přes jejich oficiální widget. **Když Dita přidá nebo upraví kočku na Peswebu, změní se i na webu.** Na web se kvůli kočkám nemusí sahat.

## Úpravy textů

Hlavička, patička i všechny stránky se generují ze souboru `tools/build.py`. Kontakty, číslo účtu a odkazy jsou nahoře v souboru. Po úpravě spusťte:

```sh
python3 tools/build.py
```

HTML soubory jdou upravovat i přímo, ale při dalším spuštění skriptu se přepíšou.

## Spuštění lokálně

```sh
python3 -m http.server 8000
# a otevřít http://localhost:8000
```

Widget Pesweb se na `localhost` načte jen s nastaveným `baseUrl`, což skript dělá.

## Nasazení na GitHub Pages

Settings → Pages → Source: *Deploy from a branch* → větev `main`, složka `/ (root)`. Soubor `.nojekyll` už v repozitáři je.

## Fotky

Fotky v `assets/img/` jsou převzaté z původního webu depozita (webnode) a zmenšené pro web. QR platba (`assets/img/qr-platba.svg`) je ve formátu SPD (QR Platba) na účet 6077760777/2010.
