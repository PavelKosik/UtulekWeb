#!/usr/bin/env python3
"""Sestaví statické HTML stránky webu Depozitum chlup-nechlup.

Spuštění:  python3 tools/build.py
Texty, kontakty a čísla se mění tady v souboru, HTML se pak vygeneruje znovu.
QR kódy se přegenerují jen tehdy, když je nainstalovaný balíček `qrcode`
(pip install qrcode); jinak se použijí ty, které už jsou v assets/img.
"""
import hashlib
import json
import pathlib
import re
import struct
import sys
from urllib.parse import quote, urlparse

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Kontakty a údaje
# ---------------------------------------------------------------------------

ORG_NAME = "Depozitum chlup - nechlup z.s."
ORG_ICO = "19405901"
ORG_SEAT = "Mutěnice 70, 386 01 Mutěnice"
ORG_REG = "spolek zapsaný ve spolkovém rejstříku u Krajského soudu v Českých Budějovicích, oddíl L, vložka 9221"
# Veřejná adresa webu (kanonické odkazy, náhledy pro sdílení, QR kódy). Při přechodu na vlastní doménu
# stačí změnit tenhle řádek, třeba na "https://www.chlupnechlup.cz/"; soubor CNAME pro GitHub Pages
# se pak vytvoří sám. Postup je v README v části „Vlastní doména“.
SITE_URL = "https://pavelkosik.github.io/UtulekWeb/"

JUSTICE_DOCS = "https://or.justice.cz/ias/ui/vypis-sl-firma?subjektId=1208050"

PHONE = "+420\u00a0607\u00a0707\u00a0537"  # nezlomitelné mezery, číslo se nerozdělí na dva řádky
PHONE_TEL = "+420607707537"
EMAIL = "ditau@email.cz"
ACCOUNT = "6077760777/2010"
IBAN = "CZ6120100000006077760777"
IBAN_PRETTY = "CZ61\u00a02010\u00a00000\u00a00060\u00a07776\u00a00777"
FIO = "https://ib.fio.cz/ib/transparent?a=6077760777"
FB = "https://www.facebook.com/depozitumchlupnechlup"
FB_DITA = "https://www.facebook.com/dita.uhrikova/"
FB_RECEIPTS = "https://www.facebook.com/media/set/?set=a.2506635422737631&amp;type=3"
FB_ALBUM = "https://www.facebook.com/media/set/?vanity=depozitumchlupnechlup&amp;set=a.3773941716006989"
IG = "https://www.instagram.com/chlupnechlup/"
PESWEB = "https://www.pesweb.cz/utulky/depozitum-chlup-nechlup"
PESWEB_CAT = "https://www.pesweb.cz/kocky-k-adopci/"

# Čísla z Pesweb.cz (stav k datu níže). Aktualizujte podle Peswebu.
ADOPTED = 396
LISTED = 65
STATS_DATE = "říjen 2026"

# Výzva nahoře na úvodní stránce. None = nezobrazovat.
APPEAL = {
    "badge": "Akutní adopce",
    "name": "Celesta",
    "slug": "celesta",
    "since": "U nás od února 2023",
    "image": "assets/img/celesta.jpg",
    "title": "Celesta hledá domov co nejdřív.",
    "text": "Trpělivá, statečná, hravá a čistotná. Od kotěte si toho hodně vytrpěla, má zdeformovanou nožičku a po vytržení zubů se jí ještě hojí dásně. Přesto baští a užívá si život. Hledá bezpečný domov v bytě nebo v domku se zabezpečenou zahradou.",
}

# Částky pro QR platbu a co za ně depozitum pořídí (podle skutečných plateb z transparentního účtu).
AMOUNTS = [
    (300, "<strong>300 Kč</strong> = tři desetilitrové pytle steliva. Jeden nás vyjde na 89 Kč."),
    (500, "<strong>500 Kč</strong> = krmení pro celé depozitum na půl dne. Za rok kočky spořádají krmivo za 380 000 Kč."),
    (1500, "<strong>1 500 Kč</strong> = kastrace jedné kočky u našeho veterináře i s kapkami proti parazitům (poslední faktura 1 385 Kč)."),
    (None, "<strong>Jakákoli částka</strong> pomáhá. Den provozu depozita stojí zhruba 1 900 Kč."),
]
DEFAULT_AMOUNT = 500

# Kam šly peníze za posledních 12 měsíců (výdaje z transparentního účtu, přibližně, říjen 2025 – říjen 2026).
SPENDING_TOTAL = 702_000
SPENDING = [
    ("Krmivo", 380_600),
    ("Veterinární péče", 172_000),
    ("Stelivo", 58_600),
    ("Drogerie a potřeby", 42_800),
    ("Doprava (benzín)", 23_900),
    ("Účetnictví", 9_900),
    ("Ostatní", 14_200),
]
CITY_MONTHLY = 20_000

# Co se v depozitu vždy hodí. Upravte podle aktuální potřeby.
WISHLIST = [
    ("Stelivo", "v 10litrových pytlích, měsíčně jich spotřebujeme kolem padesáti"),
    ("Kapsičky, konzervy a granule", "pro koťata i dospělé kočky"),
    ("Přepravky na kočky", "zapůjčené se nám ne vždy vrátí"),
    ("Odchytové klece", "na odchyt polodivokých koček, které je potřeba vykastrovat"),
    ("Antiparazitika", "proti vnitřním i vnějším parazitům"),
    ("Deky, povlečení, škrabadla a pelíšky", "deky a povlečení klidně i staré"),
]
WISHLIST_DATE = STATS_DATE

GALLERY = [
    ("ludvik-lucian", "Ludvík a Lucián", 720, 646),
    ("xia", "Xia", 540, 720),
    ("bozanek", "Božánek", 720, 540),
    ("rekord-manka", "Rekordmanka", 536, 720),
    ("wilson", "Wilson", 720, 540),
    ("zoltan-zoro", "Zoltán a Zoro", 540, 720),
    ("cernobila", "Černobílá", 720, 540),
    ("hasa-a-harf", "Haša a Harf", 542, 720),
    ("yasmin-yanis-yann-yoniel", "Yasmin, Yanis, Yann a Yoniel", 720, 540),
    ("iska", "Iška", 536, 720),
    ("tri-gracie-z-protivina", "Tři grácie z Protivína", 720, 405),
    ("janek-3984", "Janek", 540, 720),
    ("zimba", "Zimba", 720, 480),
    ("hanah", "Hanah", 536, 720),
    ("muning-micah", "Muning a Micah", 720, 540),
    ("3-smolari", "Tři smolaři", 540, 720),
    ("filipek-6301", "Filípek", 539, 720),
    ("wega-zamluvena", "Wega", 540, 720),
    ("zrzavy-krasavec", "Zrzavý krasavec", 540, 720),
    ("tara-trina-a-tristan", "Tara, Trina a Tristan", 540, 720),
]

ICON = {
    "paw": '<svg viewBox="0 0 48 48" aria-hidden="true" fill="currentColor"><ellipse cx="11" cy="20" rx="4.6" ry="6" transform="rotate(-18 11 20)"/><ellipse cx="19.5" cy="11.5" rx="4.8" ry="6.4" transform="rotate(-6 19.5 11.5)"/><ellipse cx="29.5" cy="11.5" rx="4.8" ry="6.4" transform="rotate(6 29.5 11.5)"/><ellipse cx="38" cy="20" rx="4.6" ry="6" transform="rotate(18 38 20)"/><path d="M24.5 22c-6.2 0-12.5 8.6-12.5 13.6 0 4 3.2 5.9 6.6 5.9 2.6 0 4-1.3 5.9-1.3s3.3 1.3 5.9 1.3c3.4 0 6.6-1.9 6.6-5.9C37 30.6 30.7 22 24.5 22z"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20.5s-7.5-4.4-9.3-9.6C1.5 7.4 3.8 4 7.3 4c2 0 3.6 1.1 4.7 2.7C13.1 5.1 14.7 4 16.7 4c3.5 0 5.8 3.4 4.6 6.9-1.8 5.2-9.3 9.6-9.3 9.6z"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 9.5V20h14V9.5"/><path d="M10 20v-5h4v5"/></svg>',
    "coin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="6" width="19" height="13" rx="2.5"/><path d="M2.5 10.5h19M6.5 15h3"/></svg>',
    "repeat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 2l4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="M7 22l-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>',
    "share": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>',
    "copy": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2.5"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>',
    "external": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 3h3.5l2 5-2.5 1.5a11 11 0 0 0 6.5 6.5L16 13.5l5 2V19a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.6-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.2H7.9v3h2.6V21h3z"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 20.5l1.3-4A8.5 8.5 0 1 1 8 19.6z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-1.8-1.8l.8-1-1-2z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="1" fill="currentColor" stroke="none"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>',
    "print": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M6 14h12v7H6z"/></svg>',
    "download": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M5 20h14"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    "down": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>',
    "camera": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8h3l2-3h6l2 3h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13.5" r="3.5"/></svg>',
}
PAW_PATHS = ICON["paw"][ICON["paw"].index(">") + 1:-6]

NAV = [
    ("kocky-k-adopci.html", "Kočky k adopci"),
    ("docasna-pece.html", "Dočasná péče"),
    ("nasli-jste-kocku.html", "Našli jste kočku?"),
    ("o-nas.html", "O nás"),
    ("#kontakt", "Kontakt"),
]
FOOTER_NAV = [
    ("index.html", "Úvod"),
    ("kocky-k-adopci.html", "Kočky k adopci"),
    ("nasli-domov.html", "Domov našli"),
    ("docasna-pece.html", "Dočasná péče"),
    ("nasli-jste-kocku.html", "Našli jste kočku?"),
    ("pro-obce.html", "Pro obce"),
    ("o-nas.html", "O nás"),
    ("podporte-nas.html", "Podpořte nás"),
    ("plakat.html", "Plakát k vytištění"),
]

# Písma jsou hostovaná lokálně (assets/fonts), aby web neposílal IP adresy návštěvníků Googlu.
# Otisk stylů, skriptu a písem do adresy (?v=…): GitHub Pages nechá prohlížeč držet soubory 10 minut,
# takže bez toho by se změna stylů projevila až po vynuceném obnovení stránky (Ctrl+F5).
ASSET_V = hashlib.sha1((OUT / "assets/css/style.css").read_bytes() + (OUT / "assets/js/main.js").read_bytes()).hexdigest()[:10]
FONT_V = hashlib.sha1(b"".join(f.read_bytes() for f in sorted((OUT / "assets/fonts").glob("*.woff2")))).hexdigest()[:10]
FONT_FACES = (OUT / "assets/fonts/fonts.css").read_text(encoding="utf-8")
FONT_FACES = re.sub(r"url\(([^)]+\.woff2)\)", rf"url(assets/fonts/\1?v={FONT_V})", FONT_FACES)
FONT_FACES = re.sub(r"/\*.*?\*/\s*", "", FONT_FACES, flags=re.S)
FONT_FACES = re.sub(r"\s*\n\s*", "", FONT_FACES)
FONTS = (
    # Jen latin: preload i latin-ext (č, ř, ě…) na pomalém připojení zdržel styly a hlavní fotku (Lighthouse).
    f'<link rel="preload" href="assets/fonts/fraunces-normal-latin.woff2?v={FONT_V}" as="font" type="font/woff2" crossorigin>\n'
    f'  <link rel="preload" href="assets/fonts/figtree-normal-latin.woff2?v={FONT_V}" as="font" type="font/woff2" crossorigin>\n'
    f'  <style>{FONT_FACES}</style>'
)

JSONLD = json.dumps({
    "@context": "https://schema.org",
    "@type": "AnimalShelter",
    "name": "Depozitum chlup-nechlup",
    "alternateName": ["Chlup-nechlup", "Depozitum chlup - nechlup"],
    "legalName": ORG_NAME,
    "taxID": ORG_ICO,
    "description": "Domácí depozitum pro odchyt, léčbu a kastraci koček ze Strakonic a okolí.",
    "address": {"@type": "PostalAddress", "addressLocality": "Mutěnice", "postalCode": "386 01", "addressRegion": "Jihočeský kraj", "addressCountry": "CZ"},
    "areaServed": [{"@type": "City", "name": "Strakonice"}, {"@type": "AdministrativeArea", "name": "Strakonicko"}],
    "knowsAbout": ["adopce koček", "dočasná péče o kočky", "kastrace koček", "nalezené kočky"],
    "url": SITE_URL,
    "logo": SITE_URL + "assets/img/icon-512.png",
    "image": SITE_URL + "assets/img/og/og-uvod.jpg",
    "telephone": PHONE_TEL,
    "email": EMAIL,
    "contactPoint": {"@type": "ContactPoint", "telephone": PHONE_TEL, "email": EMAIL, "contactType": "adopce a nalezené kočky", "availableLanguage": "cs"},
    "sameAs": [FB, IG, PESWEB],
}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Společné části
# ---------------------------------------------------------------------------

# Náhledový obrázek pro sdílení (1200×630) podle stránky, viz tools/og_images.js
OG = {
    "index.html": "og-uvod.jpg",
    "kocky-k-adopci.html": "og-adopce.jpg",
    "nasli-domov.html": "og-domov.jpg",
    "docasna-pece.html": "og-docaska.jpg",
    "podporte-nas.html": "og-podpora.jpg",
    "nasli-jste-kocku.html": "og-nalez.jpg",
    "pro-obce.html": "og-nalez.jpg",
}

# Skript v <head>: skryje animované prvky ještě před prvním vykreslením (bez probliknutí).
# Kdyby se main.js nenačetl, po 4 s se vše zobrazí.
HEAD_SCRIPT = (
    '<script>document.documentElement.classList.remove("js-off");'
    'setTimeout(function(){if(!window.__siteReady)document.documentElement.classList.add("js-off")},4000);</script>'
)

# Přednačtení podstránek při najetí myší (Chrome); jen vlastní stránky, nic externího.
SPECULATION = '<script type="speculationrules">{"prefetch":[{"where":{"href_matches":"*.html","relative_to":"document"},"eagerness":"moderate"}]}</script>'


def head(title, desc, current, extra_head=""):
    full = title if current == "index.html" else f"{title} · Depozitum chlup-nechlup Strakonice"
    url = SITE_URL if current == "index.html" else SITE_URL + current
    og_image = SITE_URL + "assets/img/og/" + OG.get(current, "og-uvod.jpg")
    # 404 se zobrazuje i na vnořených adresách, proto absolutní základ a žádné indexování
    base = f'\n  <base href="{SITE_URL}">\n  <meta name="robots" content="noindex">' if current == "404.html" else ""
    return f"""<!doctype html>
<html lang="cs" class="js-off">
<head>
  <meta charset="utf-8">{base}
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{url}">
  <meta name="color-scheme" content="only light">
  <meta name="theme-color" content="#f7f0e5">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:site_name" content="Depozitum chlup-nechlup">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{full}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="manifest" href="manifest.webmanifest">
  {HEAD_SCRIPT}
  {FONTS}
  <link rel="stylesheet" href="assets/css/style.css?v={ASSET_V}">
  {SPECULATION}{extra_head}
</head>
<body>
  <a class="skip-link" href="#obsah">Přeskočit na obsah</a>
  <div class="progress" aria-hidden="true"></div>
{header(current)}
  <main id="obsah">
"""


def header(current):
    cur = ' aria-current="page"'
    links = "\n".join(
        f'        <a href="{href}"{cur if href == current else ""}>{label}</a>' for href, label in NAV
    )
    return f"""  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="index.html">
        {ICON["paw"]}
        <span>chlup-nechlup<small>Depozitum pro kočky · Strakonice</small></span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="hlavni-menu"><span class="nav-toggle__bars" aria-hidden="true"></span><span class="nav-toggle__text">Menu</span></button>
      <nav class="nav" id="hlavni-menu" aria-label="Hlavní menu">
{links}
        <a class="btn" href="podporte-nas.html"{cur if current == "podporte-nas.html" else ""}>{ICON["heart"]}Podpořit</a>
        <a class="nav-phone" href="tel:{PHONE_TEL}">{ICON["phone"]}Dita: {PHONE}</a>
      </nav>
    </div>
  </header>"""


def footer(current=""):
    cta_second = f'<a class="btn" href="podporte-nas.html#dar">{ICON["heart"]}Podpořit</a>'
    if current == "kocky-k-adopci.html":
        cta_first = f'<a class="btn btn--ghost" href="#dotaznik">{ICON["heart"]}Mám zájem</a>'
    elif current == "docasna-pece.html":
        cta_first = f'<a class="btn btn--ghost" href="#prihlaska">{ICON["mail"]}Přihláška</a>'
    elif current == "nasli-jste-kocku.html":  # nálezce potřebuje telefon, ne dar
        cta_first = f'<a class="btn btn--ghost" href="tel:156">{ICON["phone"]}Volat 156</a>'
        cta_second = '<a class="btn" href="#obec-odmitla">Obec odmítla?</a>'
    else:
        cta_first = '<a class="btn btn--ghost" href="kocky-k-adopci.html">Kočky k adopci</a>'
    nav = "\n".join(f'            <li><a href="{h}">{l}</a></li>' for h, l in FOOTER_NAV)
    # na stránce s darem lišta jen překáží, dar je hned nahoře
    mobile_cta = "" if current == "podporte-nas.html" else f"""
  <nav class="mobile-cta" aria-label="Rychlé odkazy">
    {cta_first}
    {cta_second}
  </nav>
"""
    return f"""  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div>
          <p class="footer-big">Každá kočka si zaslouží teplé místo.</p>
          <p style="opacity:.8;max-width:38ch">Domácí depozitum pro odchyt a léčbu koček ze Strakonic a okolí. Fungujeme hlavně díky vašim darům.</p>
          <div class="socials">
            <a href="{FB}" target="_blank" rel="noopener" aria-label="Facebook Depozita">{ICON["fb"]}</a>
            <a href="{IG}" target="_blank" rel="noopener" aria-label="Instagram">{ICON["ig"]}</a>
            <a href="mailto:{EMAIL}" aria-label="E-mail">{ICON["mail"]}</a>
          </div>
        </div>
        <div>
          <h2 class="footer-title">Web</h2>
          <ul>
{nav}
          </ul>
        </div>
        <div id="kontakt">
          <h2 class="footer-title">Kontakt</h2>
          <ul>
            <li>Mutěnice u Strakonic</li>
            <li>Návštěvy jen po domluvě</li>
            <li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
            <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          </ul>
        </div>
        <div>
          <h2 class="footer-title">Transparentní účet</h2>
          <ul>
            <li><strong>{ACCOUNT}</strong></li>
            <li>Fio banka</li>
            <li><a href="{FIO}" target="_blank" rel="noopener">Pohyby na účtu</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© <span data-year>2026</span> {ORG_NAME} · IČO {ORG_ICO} · sídlo {ORG_SEAT} · {ORG_REG}</span>
        <span><a href="soukromi.html">Soukromí a cookies</a> · Kočky k adopci zveřejňujeme přes <a href="{PESWEB}" target="_blank" rel="noopener">Pesweb.cz</a></span>
      </div>
    </div>
  </footer>

{mobile_cta}
  <script src="assets/js/main.js?v={ASSET_V}"></script>
</body>
</html>
"""


def widget(filters, layout=None, reveal=True, more=None):
    """Widget Pesweb.cz se seznamem koček. Skript načte main.js, až když je widget na dohled.

    Patičku Peswebu („Zobrazeno 12 z 65 zvířat“ a tlačítko „Načíst další“) vypínáme, protože
    její vzhled nejde sladit s webem: widget z nastavení barev použije jen pozadí.
    U dlouhých seznamů (more = kolik koček nejvýš) si widget řekne rovnou o všechny kočky
    a web je odkrývá po částech vlastním tlačítkem. Stránka widgetu má i pro 65 koček jen
    asi 75 kB (komprimovaně) a fotky se načítají, až když se k nim návštěvník posune.
    """
    cfg = {
        "baseUrl": "https://www.pesweb.cz",
        "type": "cat",
        # showPagination musí jít přes filters: loader Peswebu dá do adresy každý klíč z filters,
        # z layoutu ale posílá jen showPagination=true.
        "filters": {"shelter": "depozitum-chlup-nechlup", **filters, "showPagination": False},
        "height": "auto",
        "theme": {"primaryColor": "#d4612a", "backgroundColor": "#fffaf2", "textColor": "#2b211b", "borderRadius": "16px"},
    }
    if more:
        layout = {**(layout or {}), "itemsPerPage": more}
    if layout:
        cfg["layout"] = layout
    data = json.dumps(cfg, ensure_ascii=False).replace("'", "&#39;")
    frame = f"""<div data-pesweb='{data}'>
            <p class="widget-fallback">Načítáme kočičky… Pokud se seznam nezobrazí, najdete je přímo na <a href="{PESWEB}" target="_blank" rel="noopener">Pesweb.cz</a>.</p>
          </div>"""
    if more:
        frame = f"""<div class="widget-clip" data-widget-clip>
          {frame}
          </div>
          <p class="widget-more" data-widget-more hidden><button class="btn btn--ghost" type="button">Zobrazit další kočky{ICON["down"]}</button></p>"""
    return f"""<div class="widget-shell{" reveal" if reveal else ""}">
          {frame}
        </div>
        <p class="widget-note">Všechny naše kočky najdete i na <a href="{PESWEB}" target="_blank" rel="noopener">Pesweb.cz</a>. Profil kočky se otevře v nové záložce.</p>"""


def share(text, url="", label="Sdílet:"):
    """Tlačítka pro sdílení. Adresa stránky se doplní v prohlížeči."""
    url_attr = f' data-url="{url}"' if url else ""
    return f"""<div class="share" data-share="{text}"{url_attr}>
          <span class="share__label">{label}</span>
          <button type="button" data-share-native>{ICON["share"]}<span>Sdílet</span></button>
          <a href="{FB}" target="_blank" rel="noopener" data-share-fb>{ICON["fb"]}Facebook</a>
          <a href="https://wa.me/" target="_blank" rel="noopener" data-share-wa>{ICON["wa"]}WhatsApp</a>
          <button type="button" data-share-copy>{ICON["copy"]}<span>Kopírovat odkaz</span></button>
        </div>"""


def qr_file(amount, ext="svg"):
    return f"assets/img/qr-platba-{amount}.{ext}" if amount else f"assets/img/qr-platba.{ext}"


def account_card(extra_class=""):
    buttons = []
    default_impact = AMOUNTS[0][1]
    for amount, impact in AMOUNTS:
        pressed = "true" if amount == DEFAULT_AMOUNT else "false"
        if amount == DEFAULT_AMOUNT:
            default_impact = impact
        label = f"{amount:,} Kč".replace(",", " ") if amount else "Jiná"
        buttons.append(
            f'<button type="button" data-amount="{amount or ""}" data-qr="{qr_file(amount)}" data-png="{qr_file(amount, "png")}" '
            f'data-impact="{impact.replace(chr(34), "&quot;")}" aria-pressed="{pressed}">{label}</button>'
        )
    return f"""<div class="account {extra_class}" data-progress>
          <div>
            <div class="account__label">Transparentní účet · Fio banka</div>
            <div class="account__number">{ACCOUNT}</div>
            <div class="account__meta">{ORG_NAME} · IBAN {IBAN_PRETTY}</div>
            <div class="amounts" data-amounts role="group" aria-label="Částka daru">
              {"".join(buttons)}
            </div>
            <p class="impact" aria-live="polite">{default_impact}</p>
            <div class="btn-row">
              <button class="btn" type="button" data-copy="{ACCOUNT}">{ICON["copy"]}<span>Kopírovat číslo účtu</span></button>
              <a class="btn btn--ghost" href="{FIO}" target="_blank" rel="noopener">Pohyby na účtu{ICON["external"]}</a>
            </div>
            <p class="mobile-hint">Platíte z mobilu? Uložte si QR kód a v aplikaci banky ho nahrajte z galerie (QR platba → z obrázku). Nebo zkopírujte číslo účtu.</p>
          </div>
          <div class="account__qr">
            <img src="{qr_file(DEFAULT_AMOUNT)}" alt="QR platba {DEFAULT_AMOUNT} Kč na transparentní účet" width="130" height="130">
            <span>QR platba {DEFAULT_AMOUNT} Kč</span>
            <a class="qr-save" href="{qr_file(DEFAULT_AMOUNT, "png")}" download="qr-platba-depozitum-{DEFAULT_AMOUNT}.png">{ICON["download"]}Uložit QR</a>
          </div>
        </div>"""


def monthly_block():
    return f"""<div class="monthly">
          <div>
            <p class="eyebrow">Trvalý příkaz</p>
            <h3 class="reveal">Nejvíc pomůže pravidelný příspěvek.</h3>
            <p class="reveal">Díky trvalému příkazu víme, s čím můžeme počítat, a můžeme vzít další kočku z ulice. Už přes 20 lidí nám takhle posílá peníze každý měsíc, většinou 100 až 500 Kč. Kdyby se jich sešlo sto po 300 Kč, pokryli by skoro všechno krmivo na měsíc.</p>
            <p class="reveal">Trvalý příkaz si nastavíte za dvě minuty a kdykoli ho můžete zrušit.</p>
          </div>
          <ol class="reveal">
            <li>V internetovém bankovnictví zvolte <strong>Trvalý příkaz</strong>.</li>
            <li>Číslo účtu: <span class="copy-field">{ACCOUNT} <button type="button" data-copy="{ACCOUNT}">Kopírovat</button></span></li>
            <li>Do zprávy pro příjemce napište své jméno, ať víme, komu poděkovat.</li>
            <li>Zvolte částku a frekvenci <strong>měsíčně</strong>. Děkujeme!</li>
          </ol>
        </div>"""


def fmt_kc(n):
    return f"{n:,}".replace(",", " ") + " Kč"


def spending_chart():
    """Pruhový graf výdajů (jedna barva, popisky přímo u pruhů, tooltip s částkou)."""
    top = max(v for _, v in SPENDING)
    rows = []
    for label, value in SPENDING:
        share = value / SPENDING_TOTAL * 100
        pct = f"{share:.0f} %" if share >= 1 else "<1 %"
        rows.append(
            f'<li class="bars__row" tabindex="0" aria-label="{label}: {fmt_kc(value)}, {pct}">'
            f'<span class="bars__label">{label}</span>'
            f'<span class="bars__track"><span class="bars__bar" style="--w:{value / top * 100:.1f}%"></span></span>'
            f'<span class="bars__value">{pct}</span>'
            f'<span class="bars__tip" aria-hidden="true">{label}: zhruba {fmt_kc(round(value, -3))}</span></li>'
        )
    return f"""<figure class="bars reveal">
          <figcaption class="bars__title">Výdaje za posledních 12 měsíců: přibližně {fmt_kc(SPENDING_TOTAL)}</figcaption>
          <ol class="bars__list">
            {"".join(rows)}
          </ol>
          <p class="note">Podle plateb na transparentním účtu, {STATS_DATE}. Částky jsou zaokrouhlené, rozdělení podle popisu plateb.</p>
        </figure>"""


def tax_box():
    return f"""<div class="mailto-box reveal">
          <h3>Potvrzení o daru pro daňové přiznání</h3>
          <p>Dary na ochranu opuštěných zvířat si můžete odečíst od základu daně, pokud za rok darujete všem organizacím dohromady aspoň 1 000 Kč nebo 2 % základu daně. Napište nám do konce ledna své jméno, adresu a e-mail a pošleme vám potvrzení. Do zprávy pro příjemce u platby prosím uveďte své jméno, abychom dar dohledali.</p>
          <a class="btn btn--ghost" href="mailto:{EMAIL}?subject=Potvrzen%C3%AD%20o%20daru">{ICON["mail"]}Požádat o potvrzení</a>
        </div>"""


def cta_band(title, text, href, label):
    return f"""<div class="cta-band reveal" data-progress>
          <div>
            <h2>{title}</h2>
            <p>{text}</p>
          </div>
          <a class="btn" href="{href}">{label}{ICON["arrow"]}</a>
          <svg class="paw-bg" viewBox="0 0 48 48" fill="currentColor" aria-hidden="true">{PAW_PATHS}</svg>
        </div>"""


def gallery_alt(name):
    group = " a " in name or "," in name or name.startswith("Tři")
    return f"{name}, {'kočky, které už našly' if group else 'kočka, která už našla'} domov"


def gallery(items, cls="", eager=0):
    """Galerie koček, které našly domov. Prvních `eager` fotek je na první obrazovce: načtou se hned
    a přednostně a nečekají na animaci odkrytí (ta by je ukázala až po spuštění skriptu)."""
    figs = "\n".join(
        f'          <figure{"" if i < eager else ' class="reveal"'} style="--d:{(i % 4) * 0.06:.2f}s"><img src="assets/img/domov/{slug}.jpg" alt="{gallery_alt(name)}" width="{w}" height="{h}"{' fetchpriority="high"' if i < eager else ' loading="lazy"'} sizes="(max-width: 520px) 92vw, (max-width: 1000px) 45vw, 270px"><figcaption>{name}</figcaption></figure>'
        for i, (slug, name, w, h) in enumerate(items)
    )
    return f'<div class="gallery {cls}">\n{figs}\n        </div>'


def appeal_block():
    if not APPEAL:
        return ""
    a = APPEAL
    return f"""
    <section class="section--tight" style="padding-top:0;padding-bottom:clamp(2.5rem,6vw,4.5rem)" aria-labelledby="vyzva-nadpis">
      <div class="wrap">
        <div class="appeal reveal">
          <div class="appeal__media"><img src="{a["image"]}" alt="{a["name"]}" loading="lazy" sizes="(max-width: 560px) 92vw, 220px"></div>
          <div>
            <span class="appeal__badge">{a["badge"]}</span>
            <h2 id="vyzva-nadpis">{a["title"]}</h2>
            <p>{a["text"]}</p>
            <p class="appeal__since">{a["since"]}</p>
          </div>
          <div class="appeal__actions">
            <a class="btn" href="kocky-k-adopci.html?kocka={quote(a["name"])}#dotaznik">{ICON["heart"]}Mám zájem</a>
            <a class="btn btn--ghost" href="tel:{PHONE_TEL}">{ICON["phone"]}Zavolat Ditě</a>
            <p class="appeal__links"><a href="{PESWEB_CAT}{a["slug"]}" target="_blank" rel="noopener">Profil na Pesweb.cz{ICON["external"]}</a> <a href="https://www.facebook.com/sharer/sharer.php?u={quote(PESWEB_CAT + a["slug"], safe="")}" target="_blank" rel="noopener">{ICON["share"]}Sdílet</a></p>
          </div>
        </div>
      </div>
    </section>"""


def chips(name, legend, options, kind="radio"):
    """Skupina čipů (radio/checkbox) pro dotazníky: options = [(hodnota, popisek)]."""
    items = "".join(f'<label><input type="{kind}" name="{name}" value="{v}"><span>{t}</span></label>' for v, t in options)
    return f'<fieldset class="chips qf"><legend>{legend}</legend>{items}</fieldset>'


def qform_actions(kind):
    subject = "Zájem o adopci" if kind == "adopce" else "Dočasná péče"
    return f"""<p class="qform__error" data-qform-error hidden role="alert"></p>
            <div class="qform__preview" data-qform-preview-wrap hidden>
              <p class="qform__label">Vaše zpráva pro Ditu</p>
              <pre data-qform-preview></pre>
            </div>
            <div class="btn-row">
              <button class="btn" type="submit" data-qform-mail data-subject="{subject}">{ICON["mail"]}<span>Odeslat e-mailem</span></button>
              <button class="btn btn--ghost qform__sms" type="button" data-qform-sms>{ICON["phone"]}<span>Poslat SMS</span></button>
              <button class="btn btn--ghost" type="button" data-qform-copy>{ICON["copy"]}<span>Zkopírovat zprávu</span></button>
            </div>
            <p class="qform__after" data-qform-after hidden role="status">Neotevřel se vám e-mail? Zkopírujte zprávu a pošlete ji ze své schránky (třeba ze Seznamu nebo Gmailu) na <strong>{EMAIL}</strong>. Nebo zavolejte na <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
            <p class="note">Formulář nic neukládá ani neodesílá. Jen z odpovědí připraví zprávu, kterou pošlete e-mailem na <strong>{EMAIL}</strong> nebo SMS, případně ji vložíte do zprávy na <a href="{FB}" target="_blank" rel="noopener">Facebooku Depozita</a>. Raději voláte? <a href="tel:{PHONE_TEL}">{PHONE}</a></p>"""


ADOPTION_FORM = f"""<form class="qform reveal" id="dotaznik" data-qform="adopce" data-to="{EMAIL}" data-sms="{PHONE_TEL}" novalidate>
            <h3>Dotazník pro zájemce</h3>
            <p class="qform__lead">Pár kliknutí místo dlouhého psaní. Na tyhle otázky se Dita stejně zeptá a díky nim vám doporučí kočku, která k vám opravdu sedne.</p>
            <label class="qf qf--text">O kterou kočičku máte zájem?<input type="text" name="kocka" placeholder="např. Celesta, nebo nechte prázdné" autocomplete="off"></label>
            {chips("bydleni", "Kde bydlíte?", [("v bytě", "V bytě"), ("v domě bez zahrady", "V domě"), ("v domě se zahradou", "V domě se zahradou")])}
            {chips("ven", "Bude kočka chodit ven?", [("bude jen doma", "Jen doma"), ("bude chodit na zabezpečenou zahradu nebo do výběhu", "Na zabezpečenou zahradu"), ("bude chodit volně ven", "Volně ven")])}
            {chips("site", "Máte okna a balkon zajištěné sítí?", [("ano", "Ano"), ("zatím ne, pořídíme", "Zatím ne, pořídíme")])}
            {chips("domacnost", "Kdo s vámi bydlí?", [("děti", "Děti"), ("další kočka", "Další kočka"), ("pes", "Pes"), ("jiná zvířata", "Jiná zvířata")], "checkbox")}
            <label class="qf qf--text" data-show-if="domacnost=děti" hidden>Kolik je dětem let?<input type="text" name="vek_deti" placeholder="např. 4 a 9 let" autocomplete="off"></label>
            {chips("zkusenosti", "Máte s kočkami zkušenosti?", [("bude to naše první kočka", "První kočka"), ("kočku jsme už měli", "Už jsme měli"), ("kočku máme i teď", "Máme i teď")])}
            {chips("sama", "Jak dlouho bude kočka přes den sama?", [("skoro vůbec", "Skoro vůbec"), ("do 4 hodin", "Do 4 hodin"), ("4 až 8 hodin", "4–8 hodin"), ("déle než 8 hodin", "Déle")])}
            <label class="qf qf--text">Kdo se o kočku postará, když budete pryč?<input type="text" name="dovolena" placeholder="např. rodiče, soused" autocomplete="off"></label>
            <label class="qf qf--text">Co od kočky čekáte? <small>(nepovinné)</small><textarea name="ocekavani" rows="2" placeholder="např. mazlivou kočku k dětem, klidnou společnici…"></textarea></label>
            <fieldset class="qf qf--contact"><legend>Kontakt, ať se vám Dita může ozvat</legend>
              <label>Jméno<input type="text" name="jmeno" autocomplete="name" required></label>
              <label>Telefon<input type="tel" name="telefon" autocomplete="tel" inputmode="tel" required></label>
              <label>Obec<input type="text" name="obec" autocomplete="address-level2"></label>
            </fieldset>
            <label class="qf qf--check"><input type="checkbox" name="podminky" value="ano" required><span>Rozumím, že kočky vydáváte na adopční smlouvu a že se u koťat zavazuji ke kastraci v dospělosti.</span></label>
            {qform_actions("adopce")}
          </form>"""

FOSTER_FORM = f"""<form class="qform reveal" id="prihlaska" data-qform="docaska" data-to="{EMAIL}" data-sms="{PHONE_TEL}" novalidate>
            <h3>Přihláška do dočasné péče</h3>
            <p class="qform__lead">Nezávazně. Dita se vám ozve a domluvíte se, jaká kočička by se k vám hodila.</p>
            {chips("bydleni", "Kde bydlíte?", [("v bytě", "V bytě"), ("v domě bez zahrady", "V domě"), ("v domě se zahradou", "V domě se zahradou")])}
            {chips("mistnost", "Máte pro kočku na začátek samostatnou místnost?", [("ano", "Ano"), ("ne", "Ne")])}
            {chips("zvirata", "Máte doma zvířata?", [("nemám", "Nemám"), ("kočku", "Kočku"), ("psa", "Psa"), ("jiná zvířata", "Jiná")], "checkbox")}
            {chips("delka", "Na jak dlouho můžete kočku vzít?", [("na pár týdnů", "Pár týdnů"), ("na 1 až 3 měsíce", "1–3 měsíce"), ("dokud nenajde domov", "Dokud nenajde domov")])}
            {chips("koho", "Koho byste si vzali nejraději?", [("koťata", "Koťata"), ("dospělou kočku", "Dospělou kočku"), ("je mi to jedno", "Je mi to jedno")])}
            <fieldset class="qf qf--contact"><legend>Kontakt</legend>
              <label>Jméno<input type="text" name="jmeno" autocomplete="name" required></label>
              <label>Telefon<input type="tel" name="telefon" autocomplete="tel" inputmode="tel" required></label>
              <label>Obec<input type="text" name="obec" autocomplete="address-level2"></label>
            </fieldset>
            <label class="qf qf--text">Chcete nám ještě něco napsat? <small>(nepovinné)</small><textarea name="poznamka" rows="2" placeholder="např. odkdy můžete, nebo na co se chcete zeptat"></textarea></label>
            {qform_actions("docaska")}
          </form>"""






def image_size(path):
    """Rozměry JPEG/WebP bez Pillow (z hlavičky souboru)."""
    data = path.read_bytes()
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", data[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            b = data[21:25]
            return 1 + (((b[1] & 0x3F) << 8) | b[0]), 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
        if kind == b"VP8X":
            return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def picture(match):
    """<img src="assets/img/x.jpg" …> → <picture> s WebP variantami (vytváří tools/optimize_images.py)."""
    tag, src = match.group(0), match.group(1)
    jpg = OUT / src
    if "data-noopt" in tag or not jpg.exists():
        return tag.replace(" data-noopt", "")
    if " width=" not in tag:
        size = image_size(jpg)
        if size:
            tag = tag.replace("<img ", f'<img width="{size[0]}" height="{size[1]}" ', 1)
    if "loading=\"lazy\"" in tag and "decoding=" not in tag:
        tag = tag.replace("<img ", '<img decoding="async" ', 1)
    variants = []
    for w in (400, 800):
        webp = jpg.with_name(f"{jpg.stem}-{w}.webp")
        if webp.exists():
            size = image_size(webp)
            variants.append(f"{src.rsplit('/', 1)[0]}/{webp.name} {size[0] if size else w}w")
    if not variants:
        return tag
    sizes = re.search(r'sizes="([^"]+)"', tag)
    sizes = sizes.group(1) if sizes else "(max-width: 860px) 92vw, 540px"
    last = re.search(r"(\d+)px\s*$", sizes)  # nad 1600 px se web zvětšuje s oknem (1rem = 1vw), obrázky taky
    if last:
        sizes = sizes[:last.start(1)] + f"(min-width: 1601px) {int(last.group(1)) / 16:g}vw, " + sizes[last.start(1):]
    tag = re.sub(r'\s*sizes="[^"]+"', "", tag)
    return f'<picture><source type="image/webp" srcset="{", ".join(variants)}" sizes="{sizes}">{tag}</picture>'


def hero_now(match):
    """Úvod stránky se ukáže hned (CSS animace), nečeká na JavaScript; zrychlí to LCP."""
    return match.group(0).replace("reveal reveal--scale", "hero-in").replace(" reveal", " hero-in").replace('class="reveal', 'class="hero-in')


NBSP = "\u00a0"
NO_TYPO = ("script", "style", "pre", "textarea", "title", "code")


def typo(html):
    """Česká typografie v textu stránky (ne v tazích, skriptech a stylech): jednopísmenná slova,
    tisíce, jednotky a paragraf se nezalomí na konci řádku; e-mail a název depozita se nerozdělí."""
    out, skip = [], 0
    for part in re.split(r"(<[^>]+>)", html):
        if part.startswith("<"):
            tag = re.match(r"</?([a-zA-Z0-9]+)", part)
            if tag and tag.group(1).lower() in NO_TYPO and not part.endswith("/>"):
                skip += -1 if part.startswith("</") else 1
            out.append(part)
            continue
        if skip or not part.strip():
            out.append(part)
            continue
        t = re.sub(r"(?<!\w)([VvKkSsZzAaIiOoUu]) (?=\S)", "\\1" + NBSP, part)
        t = re.sub(r"(\d) (?=\d{3}(?!\d))", "\\1" + NBSP, t)
        t = re.sub(r"(\d) (?=(?:Kč|%|let|roků|měsíců|dní|kusů|km|kg|m|l|h)(?!\w))", "\\1" + NBSP, t)
        t = t.replace("§ ", "§" + NBSP)
        t = re.sub(r"\b((?:e-mail|chlup-nechlup)\w*)", r'<span class="nw">\1</span>', t)
        out.append(t)
    return "".join(out)


def page(name, title, desc, body, extra_head=""):
    body = re.sub(r'<section class="(?:hero|page-hero)[^"]*">.*?</section>', hero_now, body, count=1, flags=re.S)
    body = re.sub(r'<img [^>]*src="(assets/img/[^"]+\.jpg)"[^>]*>', picture, body)
    html = typo(head(title, desc, name, extra_head) + body + footer(name))
    (OUT / name).write_text(html, encoding="utf-8")
    print("wrote", name, len(html))


def make_qr():
    try:
        import qrcode
        import qrcode.image.svg
    except ImportError:
        print("qrcode není nainstalovaný, QR kódy se nepřegenerují")
        return
    codes = {f"qr-platba-{a}.svg" if a else "qr-platba.svg": f"SPD*1.0*ACC:{IBAN}*{'AM:' + str(a) + '.00*' if a else ''}RN:DEPOZITUM CHLUP-NECHLUP*MSG:DAR PRO KOCKY*CC:CZK" for a, _ in AMOUNTS}
    codes["qr-adopce.svg"] = SITE_URL + "kocky-k-adopci.html"
    for name, data in codes.items():
        img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
        path = OUT / "assets/img" / name
        img.save(str(path))
        svg = path.read_text(encoding="utf-8")
        svg = svg.replace('width="', 'data-w="', 1).replace('height="', 'data-h="', 1)
        path.write_text(svg, encoding="utf-8")
        if name.startswith("qr-platba"):
            try:  # PNG pro uložení do telefonu (bankovní aplikace umí QR z galerie)
                qrcode.make(data, box_size=14, border=3).save(str(path.with_suffix(".png")))
            except Exception as e:  # bez Pillow se PNG nevytvoří
                print("PNG QR se nevytvořil:", e)
    print("QR kódy:", ", ".join(codes))


# ---------------------------------------------------------------------------
# Úvod
# ---------------------------------------------------------------------------

INDEX = f"""
    <section class="hero">
      <div class="hero-blob" aria-hidden="true"></div>
      <div class="wrap">
        <div>
          <p class="eyebrow reveal">Depozitum chlup-nechlup · Strakonice</p>
          <h1 class="reveal" style="--d:.08s">Hledáme ten <span class="accent-word">pravý domov</span> pro opuštěné kočky.</h1>
          <p class="lead reveal" style="--d:.16s">Odchytáváme, léčíme a kastrujeme toulavé kočky ze Strakonic a okolí. Pak jim hledáme lidi, kteří je budou mít rádi napořád.</p>
          <div class="btn-row reveal" style="--d:.24s">
            <a class="btn" href="kocky-k-adopci.html">Chci adoptovat{ICON["arrow"]}</a>
            <a class="btn btn--ghost" href="#pomoc">Chci pomoct</a>
          </div>
          <p class="hero-found reveal" style="--d:.3s"><a href="nasli-jste-kocku.html">Našli jste kočku nebo koťata?{ICON["arrow"]}</a></p>
          <ul class="hero-trust">
            <li>{ADOPTED} koček už našlo domov</li>
            <li>Adopce bez poplatku</li>
            <li>Transparentní účet</li>
          </ul>
        </div>
        <div class="collage reveal reveal--scale" style="--d:.1s" aria-hidden="true">
          <figure class="c1"><img src="assets/img/kocka-tuxedo.jpg" alt="" width="959" height="652" fetchpriority="high" sizes="(max-width: 860px) 70vw, 460px"></figure>
          <figure class="c2"><img src="assets/img/xantipa.jpg" alt="" width="527" height="938" sizes="(max-width: 860px) 40vw, 260px"></figure>
          <figure class="c3"><img src="assets/img/eliot-a-emil.jpg" alt="" width="960" height="720" sizes="(max-width: 860px) 45vw, 280px"></figure>
          <div class="sticker"><span><strong>{LISTED}</strong>koček a vrhů hledá domov</span></div>
        </div>
      </div>
      <a class="scroll-cue" href="#kocky"><i></i>Scrollujte</a>
    </section>
{appeal_block()}

    <section class="section section--tight" id="kocky" aria-labelledby="adopce-nadpis" style="padding-top:clamp(1.5rem,4vw,3rem)">
      <div class="wrap">
        <div class="section-head">
          <p class="eyebrow">Hledají domov</p>
          <h2 id="adopce-nadpis" class="reveal">Možná na vás čeká právě teď.</h2>
          <p class="lead reveal" style="--d:.08s">Seznam se načítá živě z portálu Pesweb.cz. Zaujala vás některá kočka? Ozvěte se Ditě a domluvíte se na seznámení.</p>
        </div>
        <div class="tabs" role="tablist" aria-label="Výběr koček">
          <button type="button" role="tab" id="tab-cekaji" aria-controls="panel-cekaji" aria-selected="true">Čekají nejdéle</button>
          <button type="button" role="tab" id="tab-nove" aria-controls="panel-nove" aria-selected="false" tabindex="-1">Nově v depozitu</button>
        </div>
        <div class="tab-panel" id="panel-cekaji" role="tabpanel" tabindex="0" aria-labelledby="tab-cekaji">
          <p class="tab-intro">Tyhle kočky jsou u nás nejdéle, některé i několik let. Často jsou to dospělé, plaché nebo starší kočky, které potřebují trpělivého člověka. Odmění se mu ale celou duší.</p>
          {widget({"sort": "foundDate:asc"}, {"itemsPerPage": 6, "mobileItems": 3}, reveal=False)}
        </div>
        <div class="tab-panel" id="panel-nove" role="tabpanel" tabindex="0" aria-labelledby="tab-nove" hidden>
          <p class="tab-intro">Nejnovější přírůstky, které hledají domov. Na jaře a v létě jsou to hlavně koťata.</p>
          {widget({"sort": "createdAt:desc"}, {"itemsPerPage": 6, "mobileItems": 3}, reveal=False)}
        </div>
        <div class="btn-row" style="margin-top:1.75rem">
          <a class="btn" href="kocky-k-adopci.html">Všechny kočky k adopci ({LISTED}){ICON["arrow"]}</a>
        </div>
      </div>
    </section>

    <section class="section section--tight" id="pribeh">
      <div class="wrap">
        <p class="eyebrow">Kdo jsme</p>
        <p class="statement" data-words>Jsme malé domácí depozitum, ne velký útulek. Město Strakonice pokryje zhruba třetinu nákladů, <em>zbytek krmiva, kastrací a léčení</em> platíte vy.</p>
        <div class="stats">
          <div class="stat reveal"><div class="stat__num" data-count="{ADOPTED}">{ADOPTED}</div><div class="stat__label">koček našlo domov přes Pesweb.cz</div></div>
          <div class="stat reveal" style="--d:.08s"><div class="stat__num" data-count="{LISTED}">{LISTED}</div><div class="stat__label">koček a vrhů teď hledá domov</div></div>
          <div class="stat reveal" style="--d:.16s"><div class="stat__num" data-count="20">20</div><div class="stat__label">míst v depozitu, rozdělených podle místa nálezu</div></div>
          <div class="stat reveal" style="--d:.24s"><div class="stat__num" data-count="1900">1 900</div><div class="stat__label">Kč stojí jeden den provozu: krmivo, veterina, stelivo</div></div>
        </div>
        <p class="note" style="margin-top:1rem">Čísla z Pesweb.cz a z transparentního účtu, {STATS_DATE}.</p>
      </div>
    </section>

    <section class="section section--sand" aria-labelledby="cesta-nadpis">
      <div class="wrap">
        <div class="section-head">
          <p class="eyebrow">Cesta kočky</p>
          <h2 id="cesta-nadpis">Z ulice až na gauč. Krok za krokem.</h2>
        </div>
        <div class="journey" data-journey>
          <div class="journey__media" aria-hidden="true">
            <span class="journey__label">Odchyt</span>
            <img src="assets/img/odchyt.jpg" alt="" class="is-active" loading="lazy" sizes="540px">
            <img src="assets/img/kocka-cerna.jpg" alt="" loading="lazy" sizes="540px">
            <img src="assets/img/cassie.jpg" alt="" loading="lazy" sizes="540px">
            <img src="assets/img/eliot-a-emil.jpg" alt="" loading="lazy" sizes="540px">
            <img src="assets/img/kote-choi.jpg" alt="" loading="lazy" sizes="540px">
            <div class="journey__meter"><span></span><span></span><span></span><span></span><span></span></div>
          </div>
          <ol class="journey__steps">
            <li class="journey__step is-active" data-label="Odchyt">
              <img class="mobile-img" sizes="92vw" src="assets/img/odchyt.jpg" alt="Kočka v přepravce po odchytu" loading="lazy">
              <h3>Odchyt</h3>
              <p>Sbíráme celé vrhy, dohledáváme a po nocích naháníme kočky, které se ocitly na ulici. Často čekají u nálezců nebo tam, kam je chodí krmit hodní lidé.</p>
            </li>
            <li class="journey__step" data-label="Karanténa a léčba">
              <img class="mobile-img" sizes="92vw" src="assets/img/kocka-cerna.jpg" alt="Černá kočka v karanténní kleci" loading="lazy">
              <h3>Karanténa a léčba</h3>
              <p>Každá kočka projde karanténou. Kočky z různých lokalit ubytováváme odděleně a přísně dbáme na hygienu, aby se nemoci nepřenášely.</p>
            </li>
            <li class="journey__step" data-label="Kastrace">
              <img class="mobile-img" sizes="92vw" src="assets/img/cassie.jpg" alt="Želvovinová kočka Cassie" loading="lazy">
              <h3>Kastrace</h3>
              <p>Bez kastrace se koloběh nových vrhů nezastaví. Dospělé kočky od nás odcházejí kastrované, u koťat je kastrace v dospělosti podmínkou adopce.</p>
            </li>
            <li class="journey__step" data-label="Dočasná péče">
              <img class="mobile-img" sizes="92vw" src="assets/img/eliot-a-emil.jpg" alt="Koťata Eliot a Emil" loading="lazy">
              <h3>Dočasná péče</h3>
              <p>Zdravé kočky se stěhují do dočasných domovů. Tam se mazlí, zvykají si na lidi a my je díky tomu líp poznáme.</p>
            </li>
            <li class="journey__step" data-label="Nový domov">
              <img class="mobile-img" sizes="92vw" src="assets/img/kote-choi.jpg" alt="Kotě Choi v novém domově" loading="lazy">
              <h3>Nový domov</h3>
              <p>Hledáme pro každou kočku spřízněnou duši: stabilní a bezpečný domov na adopční smlouvu. A uvolněné místo hned obsadí další kočka z ulice.</p>
              <div class="btn-row"><a class="btn" href="#kocky">Kdo hledá domov{ICON["arrow"]}</a></div>
            </li>
          </ol>
        </div>
      </div>
    </section>

    <section class="section" id="pomoc" aria-labelledby="pomoc-nadpis">
      <div class="wrap">
        <div class="section-head section-head--center">
          <p class="eyebrow">Pomáhejte s námi</p>
          <h2 id="pomoc-nadpis" class="reveal">Pomoct se dá i bez kočky doma.</h2>
          <p class="lead reveal" style="--d:.08s">Každá z těchto možností pomáhá kočkám, které zrovna čekají venku.</p>
        </div>
        <div class="help-grid">
          <a class="help-card reveal" href="kocky-k-adopci.html">
            <div class="help-card__icon">{ICON["home"]}</div>
            <h3>Adoptujte</h3>
            <p>Dejte kočce stabilní a bezpečný domov. Adopce je bez poplatku a pomůžeme vám vybrat kočku, která sedne k vaší domácnosti.</p>
            <span class="help-card__more">Jak adopce probíhá{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.08s" href="docasna-pece.html">
            <div class="help-card__icon">{ICON["paw"]}</div>
            <h3>Dočasná péče</h3>
            <p>Mějte kočku doma bez závazku na celý život. Krmení, stelivo i veterinu hradí depozitum, Dita je vám na telefonu.</p>
            <span class="help-card__more">Jak funguje dočasná péče{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.16s" href="#dar">
            <div class="help-card__icon">{ICON["repeat"]}</div>
            <h3>Pravidelný příspěvek</h3>
            <p>Pravidelný příspěvek trvalým příkazem nám pomáhá nejvíc. I 200 Kč měsíčně je znát. Účet je transparentní.</p>
            <span class="help-card__more">Nastavit trvalý příkaz{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.24s" href="podporte-nas.html#sdileni">
            <div class="help-card__icon">{ICON["share"]}</div>
            <h3>Sdílejte</h3>
            <p>Sdílejte kočičky, pověste plakát u veterináře nebo na obecní nástěnce. Čím víc lidí kočku uvidí, tím dřív najde domov.</p>
            <span class="help-card__more">Plakát a sdílení{ICON["arrow"]}</span>
          </a>
        </div>
      </div>
    </section>

    <section class="section section--dark" id="dar" aria-labelledby="dar-nadpis">
      <div class="wrap">
        <div class="donate">
          <div>
            <p class="eyebrow">Finanční dar</p>
            <h2 id="dar-nadpis" class="reveal">Peníze jdou na kočky, ne na mzdy. A je to vidět.</h2>
            <p class="lead reveal" style="--d:.08s">Jdou na krmivo, veterinu a stelivo. Účet je transparentní, každý pohyb si můžete zkontrolovat. Účtenky z nákupů sdílíme na Facebooku.</p>
            <p class="reveal soft" style="--d:.12s">Vyberte částku, naskenujte QR kód v aplikaci své banky a je hotovo.</p>
          </div>
          {account_card("reveal")}
        </div>
        {monthly_block()}
      </div>
    </section>

    <section class="section" aria-labelledby="domov-nadpis">
      <div class="wrap">
        <div class="split" style="margin-bottom:clamp(2rem,5vw,3.5rem)">
          <div>
            <p class="eyebrow">Domov našli</p>
            <h2 id="domov-nadpis" class="reveal"><span class="big-number" data-count="{ADOPTED}">{ADOPTED}</span> koček už má svého člověka.</h2>
          </div>
          <div>
            <p class="lead reveal">Za každým číslem je kočka, která začínala ve slepičárně, ve sklepě nebo u silnice. Dnes spí na gauči. Všem novým páníčkům děkujeme.</p>
            <a class="btn btn--ghost reveal" href="nasli-domov.html">Další šťastné konce{ICON["arrow"]}</a>
          </div>
        </div>
        {gallery(GALLERY[:8], "gallery--home")}
      </div>
    </section>

    <section class="section section--sand" aria-labelledby="nalez-nadpis">
      <div class="wrap">
        <div class="split split--top">
          <div>
            <p class="eyebrow">Našli jste kočku?</p>
            <h2 id="nalez-nadpis" class="reveal">Nejdřív volejte obec. Ze zákona.</h2>
            <p class="lead reveal" style="--d:.08s">Nález zvířete, které zjevně mělo majitele, musíte ohlásit obci (§ 1058 občanského zákoníku) a obec se o ně musí postarat, o kočku stejně jako o psa. Každá nenahlášená kočka znamená, že obec „problém s kočkami nemá“.</p>
            <div class="btn-row reveal" style="--d:.16s">
              <a class="btn btn--ghost" href="nasli-jste-kocku.html">Celý postup krok za krokem{ICON["arrow"]}</a>
              <a class="btn btn--ghost" href="nasli-jste-kocku.html#ztracena">Ztratila se vám kočka?</a>
            </div>
          </div>
          <div class="found-steps" style="grid-template-columns:1fr">
            <div class="found-step reveal"><h3>Městská policie</h3><p>Kde ji mají, volejte <a href="tel:156"><strong>156</strong></a>. Vždy na místě nálezu, ne do jiného města.</p></div>
            <div class="found-step reveal" style="--d:.08s"><h3>Starosta nebo odbor životního prostředí</h3><p>Kde městská policie není, najděte si číslo na starostu obce. Klidně večer nebo v neděli.</p></div>
            <div class="found-step reveal" style="--d:.16s"><h3>Teprve potom útulek</h3><p>Když obec odmítne, ozvěte se nám. Poradíme a pomůžeme s jednáním s obcí.</p></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="dita-nadpis">
      <div class="wrap">
        <div class="split">
          <div class="split__media reveal" data-progress><img sizes="(max-width: 860px) 92vw, 540px" src="assets/img/kocka-tuxedo.jpg" alt="Černobílá kočka Zina odpočívá na dece v depozitu" loading="lazy"></div>
          <div>
            <p class="eyebrow">Srdce depozita</p>
            <h2 id="dita-nadpis" class="reveal">Za vším stojí Dita.</h2>
            <p class="reveal" style="--d:.06s">Depozitum vzniklo jako malé rodinné zázemí pro nalezené kočky z okolí. Založila ho a vede <strong>Dita Uhriková</strong>. Už patnáct let se stará o nemocné a zraněné kočky, protože Strakonice pořád nemají kočičí útulek.</p>
            <p class="reveal" style="--d:.12s">Pokud se rozhodnete kočku adoptovat nebo jste nějakou našli, budete jednat právě s ní.</p>
            <div class="btn-row reveal" style="--d:.18s">
              <a class="btn" href="o-nas.html">Náš příběh{ICON["arrow"]}</a>
              <a class="btn btn--ghost" href="{FB_DITA}" target="_blank" rel="noopener">Ditin profil na FB{ICON["external"]}</a>
            </div>
          </div>
        </div>
      </div>
    </section>

"""

# ---------------------------------------------------------------------------
# Kočky k adopci
# ---------------------------------------------------------------------------

ADOPCE = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">Kočky k adopci · Strakonice</p>
        <h1 class="reveal" style="--d:.06s">Najděte svou <span class="accent-word">spřízněnou duši</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Adopce je bez poplatku. Chceme jen jedno: aby kočka našla stabilní a bezpečný domov, ve kterém zůstane napořád.</p>
        <ul class="pill-row reveal" style="--d:.18s">
          <li>{ICON["check"]}Bez poplatku</li>
          <li>{ICON["check"]}Dospělé kočky odcházejí kastrované</li>
          <li>{ICON["check"]}Na adopční smlouvu</li>
          <li>{ICON["check"]}Poradíme i po adopci</li>
        </ul>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0" aria-labelledby="postup-nadpis">
      <div class="wrap">
        <h2 id="postup-nadpis" class="visually-hidden">Jak adopce probíhá</h2>
        <ol class="process">
          <li class="reveal"><h3>Vyberte si</h3><p>Prohlédněte si kočky níže nebo v <a href="{FB_ALBUM}" target="_blank" rel="noopener">albu na Facebooku</a>. Vybrat si můžete i víc koček, poradíme, která se k vám hodí.</p></li>
          <li class="reveal" style="--d:.06s"><h3>Ozvěte se Ditě</h3><p>Zavolejte na <a href="tel:{PHONE_TEL}">{PHONE}</a> nebo <a href="#dotaznik">vyplňte krátký dotazník</a> (2 minuty). Řekněte nám něco o své domácnosti.</p></li>
          <li class="reveal" style="--d:.12s"><h3>Seznamte se</h3><p>Domluvíte si návštěvu a kočičku poznáte osobně. Dejte si čas na rozmyšlenou.</p></li>
          <li class="reveal" style="--d:.18s"><h3>Cesta domů</h3><p>Podepíšeme adopční smlouvu a kočička jede domů. Pokud si nebudete vědět rady, jsme tu dál.</p></li>
        </ol>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0" aria-label="Kočky k adopci">
      <div class="wrap">
        <div class="cat-filters" data-cat-filters role="group" aria-label="Výběr koček">
          <fieldset class="chips">
            <legend>Věk</legend>
            <label><input type="radio" name="vek" value="" checked><span>Všechny</span></label>
            <label><input type="radio" name="vek" value="kotata" data-api="0m-12m"><span>Koťata do 1 roku</span></label>
            <label><input type="radio" name="vek" value="dospele" data-api="1y-8y"><span>Dospělé (1–8 let)</span></label>
            <label><input type="radio" name="vek" value="seniori" data-api="8y"><span>Senioři (8+ let)</span></label>
          </fieldset>
          <fieldset class="chips">
            <legend>Pohlaví</legend>
            <label><input type="radio" name="pohlavi" value="" checked><span>Kočky i kocouři</span></label>
            <label><input type="radio" name="pohlavi" value="kocka" data-api="kocka"><span>Kočky</span></label>
            <label><input type="radio" name="pohlavi" value="kocour" data-api="kocour"><span>Kocouři</span></label>
          </fieldset>
          <fieldset class="chips">
            <legend>Řazení</legend>
            <label><input type="radio" name="razeni" value="" data-api="createdAt:desc" checked><span>Nejnovější</span></label>
            <label><input type="radio" name="razeni" value="nejdele" data-api="foundDate:asc"><span>Čekají nejdéle</span></label>
          </fieldset>
        </div>
        <p class="tab-intro" data-filter-note hidden>Dospělé a starší kočky čekají nejdéle. Přitom bývají klidnější a víte přesně, jakou povahu si domů berete.</p>
        <p class="filter-empty" data-filter-empty hidden role="status">Tomuhle výběru teď žádná kočka neodpovídá. Zkuste jiný filtr, nebo <a href="tel:{PHONE_TEL}">zavolejte Ditě</a>, ráda poradí, která by se k vám hodila.</p>
        {widget({"sort": "createdAt:desc"}, reveal=False, more=100)}
      </div>
    </section>

    <section class="section section--sand">
      <div class="wrap">
        <div class="split split--top split--form">
          <div>
            <p class="eyebrow">Než se ozvete</p>
            <h2 class="reveal">Pár všetečných otázek</h2>
            <ul class="checklist reveal">
              <li><span>Máte nachystaná škrabadla, misky a záchůdky?</span></li>
              <li><span>Spočítali jste si, kolik vyjde kvalitní krmení a veterina?</span></li>
              <li><span>Máte zabezpečený balkon a okna?</span></li>
              <li><span>Víte, kdo se o kočičku postará, když budete na dovolené?</span></li>
            </ul>
            <p class="reveal">Kočky vydáváme na <strong>adopční smlouvu</strong>, ve které se zavazujete poskytnout kočce stabilní a bezpečný domov. U koťat se zavazujete ke <strong>kastraci v dospělosti</strong>. Prosíme o závazné rozhodnutí; kočička u nás pár dní i týdnů v pořádku vydrží.</p>
          </div>
          {ADOPTION_FORM}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap wrap--narrow">
        <div class="section-head">
          <p class="eyebrow">Jak hledáme správný domov</p>
          <h2 class="reveal">Hledáme pro kočku domov, kde vydrží napořád.</h2>
          <p class="lead reveal">Někdy vám doporučíme jinou kočičku, než jakou jste si vybrali. Není to proto, že bychom vám nevěřili. Kočky z ulice mají své příběhy, zvyky i zdravotní omezení a chceme, aby nový domov vyšel kočce i vám. Nejčastěji jde o tyhle situace:</p>
        </div>
        <div class="faq reveal">
          <details>
            <summary>Je adopce opravdu zdarma?</summary>
            <div class="faq__body"><p>Ano. Za kočku ani za kotě od nás nic neplatíte. Podepíšeme adopční smlouvu a u koťat se zavazujete ke kastraci v dospělosti.</p></div>
          </details>
          <details>
            <summary>Jsem starší, můžu si kočku vzít?</summary>
            <div class="faq__body"><p>Ano. Doporučíme vám klidnou dospělou kočku, která se k vám hodí, a domluvíme se, kdo by se o ni postaral, kdybyste nemohli.</p></div>
          </details>
          <details>
            <summary>Pes na zahradě a kočka zvyklá chodit ven</summary>
            <div class="faq__body"><p>Starší kočky, které žily venku, psy snášejí špatně. I když si na nový domov zvyknou, zahradě se pak vyhýbají a v lepším případě se nakonec ubytují u sousedů. Rádi vám doporučíme kočku, která psy zná.</p></div>
          </details>
          <details>
            <summary>Malé děti</summary>
            <div class="faq__body"><p>Chcete dětem pořídit mazlíčka a víte, že odpovědnost nesete vy? Výborně. Pokud jste vybrali kočičku, která se do rušnější domácnosti nehodí, doporučíme jinou, které děti nevadí.</p><p>Malé děti často neznají svou sílu. K nim proto doporučíme kočku, které ruch nevadí, a poradíme, jak je spolu seznámit. Někdy, třeba u plachých koček, je lepší počkat, až děti povyrostou.</p></div>
          </details>
          <details>
            <summary>Bydlení u rušné silnice</summary>
            <div class="faq__body"><p>Dospělou kočku zvyklou chodit ven ani příliš důvěřivé kotě nedáváme k rušnější silnici. Někdy ani ke klidné cestě, pokud by ji kočka musela často přebíhat, třeba za myšmi na pole. Starší kočky si na nové hrozby zvykají těžko.</p><p>Občas se v depozitu objeví „vítací kotě“, které radostně běží ke všem lidem. Takové rádi dáme do bytu k rodině s dětmi.</p></div>
          </details>
          <details>
            <summary>Další kočky v domácnosti a zdraví</summary>
            <div class="faq__body"><p>Většina koček z depozita pochází z kočičích kolonií, takže bývají k ostatním kočkám nekonfliktní. Když ale jedna kočka z lokality měla rýmu, chřipku nebo plíseň, často se nemoc postupně projeví i u ostatních z téhož místa. Kočku z takové lokality proto nedoporučíme do domácnosti s dalšími kočkami.</p><p>Většina kočičích nemocí se na lidi nepřenáší, s výjimkou některých plísní.</p></div>
          </details>
        </div>
      </div>
    </section>

    <section class="section section--sand section--tight" aria-labelledby="po-adopci">
      <div class="wrap">
        <div class="split split--top">
          <div>
            <p class="eyebrow">Po adopci nejste sami</p>
            <h2 id="po-adopci" class="reveal">První dny doma</h2>
            <p class="reveal">Kočka z depozita potřebuje čas. Některé se první dny schovávají, jiné se hned rozvalí na gauči. Obojí je normální.</p>
            <p class="reveal">Když si nebudete vědět rady, třeba s čistotností nebo s tím, že se kočka nechce ukázat, <strong>zavolejte Ditě</strong>. Raději hned, než aby se problém zhoršil.</p>
          </div>
          <ul class="checklist reveal" style="--d:.08s">
            <li><span>Připravte jednu klidnou místnost s miskami, záchůdkem a úkrytem.</span></li>
            <li><span>Nechte kočku, ať si prostor prozkoumá sama. Nenuťte ji k mazlení.</span></li>
            <li><span>První týdny ji nepouštějte ven, nejdřív si musí zvyknout na nový domov.</span></li>
            <li><span>Zabezpečte okna a balkon sítí, i když jde o „bytovou“ kočku.</span></li>
            <li><span>Pošlete nám fotku, až se zabydlí. Moc nás to potěší.</span></li>
          </ul>
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        {cta_band("Nemůžete si teď vzít kočku natrvalo?", "Zkuste dočasnou péči. Kočce dáte domov na přechodnou dobu a náklady hradí depozitum.", "docasna-pece.html", "Dočasná péče")}
      </div>
    </section>
"""

# ---------------------------------------------------------------------------
# Domov našli
# ---------------------------------------------------------------------------

NASLI = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">Domov našli</p>
        <h1 class="reveal" style="--d:.06s"><span class="big-number" data-count="{ADOPTED}">{ADOPTED}</span> koček už má <span class="accent-word">svého člověka</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Tolik našich svěřenců eviduje Pesweb.cz jako „našel domov“ ({STATS_DATE}). Všem novým páníčkům děkujeme a přejeme mnoho radostných chvil.</p>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        {gallery(GALLERY, eager=1)}
      </div>
    </section>

    <section class="section section--sand section--tight">
      <div class="wrap">
        <div class="split">
          <div>
            <p class="eyebrow">Adoptovali jste od nás?</p>
            <h2 class="reveal">Pošlete nám fotku z nového domova.</h2>
            <p class="reveal">Nic nás nepotěší víc. A fotky spokojených koček pomáhají dalším kočkám najít domov, protože lidé vidí, že to funguje.</p>
          </div>
          <div class="btn-row reveal">
            <a class="btn" href="mailto:{EMAIL}?subject=Fotka%20z%20nov%C3%A9ho%20domova">{ICON["mail"]}Poslat fotku e-mailem</a>
            <a class="btn btn--ghost" href="{FB}" target="_blank" rel="noopener">{ICON["fb"]}Napsat na Facebook</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        <div class="section-head">
          <p class="eyebrow">Nejnovější šťastné konce</p>
          <h2 class="reveal">Kdo odešel domů naposledy</h2>
        </div>
        {widget({"statusRelease": ["nasel-domov"], "sort": "updatedAt:desc"}, more=48)}
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        {cta_band("Další kočky ještě čekají.", "Uvolněné místo v depozitu hned obsadí další kočka z ulice. Možná bude ta příští právě vaše.", "kocky-k-adopci.html", "Kočky k adopci")}
      </div>
    </section>
"""

# ---------------------------------------------------------------------------
# Dočasná péče
# ---------------------------------------------------------------------------

DOCASKA = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">Domácí depozita</p>
        <h1 class="reveal" style="--d:.06s">Dočasná péče: kočka doma <span class="accent-word">bez závazku na celý život</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Díky každému dočasnému domovu můžeme vzít z ulice další kočku. Vy dáte kočce domov na přechodnou dobu, my hradíme krmení, stelivo i veterinu.</p>
        <div class="btn-row reveal" style="--d:.18s">
          <a class="btn" href="#prihlaska">{ICON["mail"]}Chci se přihlásit</a>
          <a class="btn btn--ghost" href="tel:{PHONE_TEL}">{ICON["phone"]}{PHONE}</a>
        </div>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        <div class="layout-aside">
          <div class="prose">
            <figure><img src="assets/img/eliot-a-emil.jpg" alt="Koťata Eliot a Emil na škrabadle" fetchpriority="high" width="960" height="720" sizes="(max-width: 960px) 92vw, 720px"><figcaption>Eliot a Emil už mají domov</figcaption></figure>

            <h2>Proč dočasná péče pomáhá</h2>
            <ul>
              <li>Uvolníte místo v depozitu pro kočku, která zrovna čeká na ulici nebo u nálezce.</li>
              <li>Kočka má celého človíčka na hraní a drbání jen pro sebe, víc se mazlí a zvyká si na lidi.</li>
              <li>V domácím prostředí ji poznáte líp než my v depozitu s dvaceti kočkami. Můžeme tak doplnit její profil a najít jí ty nejlepší zájemce.</li>
              <li>Doma uděláte víc a hezčích fotek. A kočky vyfocené doma lidé sdílejí mnohem víc.</li>
            </ul>

            <div class="callout">
              <p><strong>Náklady hradí depozitum.</strong> Všechny materiální potřeby koček v dočasné péči platí Depozitum chlup-nechlup. Do dočasek navíc dáváme zdravé kočky, takže se nemusíte bát běhání po veterinách.</p>
            </div>

            <h2>Dočasná péče není půjčovna koček</h2>
            <p>Dočaskář se zavazuje starat se o kočku, dokud nenajde nový domov, nebo alespoň do doby, než se uvolní místo v depozitu. Ve chvíli, kdy kočku dáme do dočasné péče, totiž bereme z ulice další kočky: nemocné, v akutním ohrožení života nebo takové, které už čekají u nálezců.</p>
            <p>Proto není možné vrátit kočku z dočasné péče ze dne na den. Její místo mezitím zabrala kočka z ulice v karanténě a jednotlivá místa jsou rozdělena podle lokality nálezu, aby se při skrytých infekcích nenakazilo celé depozitum. Navíc je každé stěhování pro kočku velký stres.</p>
            <p>Máme i ostřílené dočaskáře, kteří si vezmou těžší případy a v klidu je vypiplají. Patří jim za to naše velké díky.</p>
          </div>
          <aside class="aside-card reveal">
            <h3>Chcete kočce dát dočasný domov?</h3>
            <p>Ozvěte se Ditě. Domluvíte se, jaká kočička by se k vám hodila a co všechno budete potřebovat.</p>
            <div class="btn-row" style="flex-direction:column">
              <a class="btn" href="#prihlaska">{ICON["mail"]}Vyplnit přihlášku</a>
              <a class="btn btn--ghost" href="tel:{PHONE_TEL}">{ICON["phone"]}{PHONE}</a>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <section class="section section--sand">
      <div class="wrap wrap--narrow">
        <div class="section-head">
          <p class="eyebrow">Na co se lidé ptají</p>
          <h2 class="reveal">Obavy, které má skoro každý</h2>
        </div>
        <div class="faq reveal">
          <details>
            <summary>Co když se do kočky zamiluju?</summary>
            <div class="faq__body"><p>To se stává a je to dobře. Znamená to, že se kočce u vás dařilo. Řekněte to Ditě: dočaskář kočku zná nejlíp, takže se o adopci můžete rovnou pobavit. A když si ji nenecháte, pomůžete nám najít jí domov, kde bude stejně šťastná.</p></div>
          </details>
          <details>
            <summary>Kolik času mi to zabere?</summary>
            <div class="faq__body"><p>Asi jako vlastní kočka: krmení, záchůdek a hlavně pozornost a mazlení. Nic navíc. Do dočasné péče dáváme hlavně zdravé kočky. Na očkování a kontroly u veterináře se domluvíme, léčení většinou nečekejte.</p></div>
          </details>
          <details>
            <summary>Na jak dlouho to je?</summary>
            <div class="faq__body"><p>Dokud kočka nenajde nový domov, nebo dokud se neuvolní místo v depozitu. Kočky z dočasné péče nabízíme k adopci přednostně. Délku pobytu i to, co dělat, kdyby se něco změnilo, si s Ditou domluvíte předem.</p></div>
          </details>
          <details>
            <summary>Už mám doma kočku nebo psa</summary>
            <div class="faq__body"><p>Napište nám, jaká zvířata doma máte. Kočku k vám vybereme tak, aby to fungovalo, a poradíme, jak je spolu seznámit. Na začátek se hodí mít pro kočku samostatnou místnost.</p></div>
          </details>
          <details>
            <summary>Kdo mi poradí, když si nebudu vědět rady?</summary>
            <div class="faq__body"><p>Dita. Je na telefonu <a href="tel:{PHONE_TEL}">{PHONE}</a> a s kočkami pracuje už patnáct let.</p></div>
          </details>
          <details>
            <summary>Co když pojedu na dovolenou?</summary>
            <div class="faq__body"><p>Řekněte nám to s předstihem a domluvíme se. Jen prosím ne ze dne na den, viz „Dočasná péče není půjčovna koček“ výše.</p></div>
          </details>
        </div>
      </div>
    </section>

    <section class="section section--tight" aria-label="Přihláška do dočasné péče">
      <div class="wrap wrap--narrow">
        {FOSTER_FORM}
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap wrap--narrow center">
        <p class="eyebrow" style="justify-content:center">Pošlete dál</p>
        <h2 class="reveal">Znáte někoho, kdo by mohl kočce dát dočasný domov?</h2>
        <p class="lead reveal" style="margin-inline:auto;max-width:52ch">Pošlete mu tuhle stránku. Třeba kamarádce, která má ráda kočky, ale vlastní si zatím pořídit nemůže.</p>
        <div class="reveal" style="display:flex;justify-content:center;margin-top:1.25rem">{share("Dočasná péče o kočky z Depozita chlup-nechlup. Náklady hradí depozitum, ty dáš kočce domov na přechodnou dobu.")}</div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        {cta_band("Dočasnou péči nezvládnete? I tak můžete pomoct.", "Pravidelný příspěvek na transparentní účet pokryje kastrace, léky i krmení.", "podporte-nas.html", "Podpořte nás")}
      </div>
    </section>
"""

# ---------------------------------------------------------------------------
# Podpořte nás
# ---------------------------------------------------------------------------

wishlist_items = "\n".join(f"          <li class=\"reveal\"><strong>{a}</strong><span>{b}</span></li>" for a, b in WISHLIST)

PODPORA = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">Podpořte nás</p>
        <h1 class="reveal" style="--d:.06s">Bez vás by depozitum <span class="accent-word">nemohlo fungovat</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Provoz depozita stojí zhruba 1 900 Kč denně. Město Strakonice nám od roku 2024 přispívá {fmt_kc(CITY_MONTHLY)} měsíčně, což pokryje zhruba třetinu nákladů. Zbytek, přes 450 000 Kč ročně, dáváte vy.</p>
      </div>
    </section>

    <section class="section section--dark section--tight" id="dar">
      <div class="wrap">
        <div class="donate">
          <div>
            <p class="eyebrow">Transparentní účet</p>
            <h2 class="reveal">Pošlete dar na kočičí účet</h2>
            <p class="lead reveal">Majitel účtu: {ORG_NAME}, IČO {ORG_ICO}. Pohyby na účtu si můžete kdykoli prohlédnout na stránkách Fio banky.</p>
            <p class="reveal soft">Ne všechny nákupy pro kočičky jsou z výpisu snadno čitelné, a proto na Facebooku sdílíme i účtenky a faktury v albu <a href="{FB_RECEIPTS}" target="_blank" rel="noopener">Transparentní účet</a>.</p>
          </div>
          {account_card("reveal")}
        </div>
        {monthly_block()}
      </div>
    </section>

    <section class="section" id="kam-jdou-penize" aria-labelledby="penize-nadpis">
      <div class="wrap">
        <div class="split split--top">
          <div>
            <p class="eyebrow">Kam jdou vaše peníze</p>
            <h2 id="penize-nadpis" class="reveal">Víc než polovina na krmivo, čtvrtina na veterinu.</h2>
            <p class="reveal">Z účtu neplatíme žádné mzdy. Peníze jdou na kočky a kontrolovat to můžete sami:</p>
            <ul class="checklist reveal">
              <li><span><a href="{FIO}" target="_blank" rel="noopener">Transparentní účet u Fio banky</a> se všemi platbami</span></li>
              <li><span><a href="{FB_RECEIPTS}" target="_blank" rel="noopener">Účtenky a faktury</a> v albu na Facebooku</span></li>
              <li><span><a href="{JUSTICE_DOCS}" target="_blank" rel="noopener">Účetní závěrky spolku</a> ve sbírce listin na justice.cz</span></li>
            </ul>
            {tax_box()}
          </div>
          {spending_chart()}
        </div>
      </div>
    </section>

    <section class="section section--sand section--tight" aria-labelledby="dekujeme-nadpis">
      <div class="wrap wrap--narrow center">
        <p class="eyebrow" style="justify-content:center">Děkujeme</p>
        <h2 id="dekujeme-nadpis" class="reveal">Pomáhají nám</h2>
        <p class="lead reveal" style="margin-inline:auto;max-width:60ch"><strong>Město Strakonice</strong>, se kterým máme od roku 2024 smlouvu, spolek <a href="https://www.pomahejmezviratum.cz/" target="_blank" rel="noopener">Pomáhejme zvířatům</a>, který nám přispěl z celostátní sbírky Den zvířat, a hlavně stovky lidí, kteří posílají dary, krmení a sdílejí naše kočky.</p>
      </div>
    </section>

    <section class="section" id="potreby" aria-labelledby="potreby-nadpis">
      <div class="wrap">
        <div class="section-head">
          <p class="eyebrow">Věcné dary</p>
          <h2 id="potreby-nadpis" class="reveal">Co se v depozitu vždy hodí</h2>
          <p class="lead reveal">Než něco koupíte, napište nebo zavolejte Ditě. Řekne vám, co zrovna dochází, a domluvíte se na předání.</p>
        </div>
        <ul class="wishlist">
{wishlist_items}
        </ul>
        <div class="btn-row">
          <a class="btn" href="mailto:{EMAIL}?subject=V%C4%9Bcn%C3%BD%20dar">{ICON["mail"]}Domluvit věcný dar</a>
          <a class="btn btn--ghost" href="tel:{PHONE_TEL}">{ICON["phone"]}{PHONE}</a>
        </div>
        <p class="note" style="margin-top:0.875rem">Podle toho, o co depozitum žádá na Peswebu a co nejčastěji kupuje (transparentní účet, {WISHLIST_DATE}).</p>
      </div>
    </section>

    <section class="section section--sand" id="sdileni" aria-labelledby="sdileni-nadpis">
      <div class="wrap">
        <div class="split split--top">
          <div>
            <p class="eyebrow">Sdílení</p>
            <h2 id="sdileni-nadpis" class="reveal">Nic nestojí a moc pomáhá</h2>
            <p class="reveal">Kočky, které vidí víc lidí, najdou domov rychleji.</p>
            <ul class="checklist reveal">
              <li><span>Sdílejte jednu kočičku týdně z <a href="{FB}" target="_blank" rel="noopener">Facebooku Depozita</a>.</span></li>
              <li><span>Vytiskněte plakát a pověste ho u veterináře, v obchodě nebo na obecní nástěnce.</span></li>
              <li><span>Máte web obce, ordinace nebo firmy? Kočky na něj můžete vložit přes Pesweb.cz. <a href="mailto:{EMAIL}?subject=Inzerce%20ko%C4%8Dek">Napište nám</a>.</span></li>
            </ul>
          </div>
          <div class="quote-card reveal" style="--d:.08s">
            <h3>Plakát „Hledáme domov“</h3>
            <p style="color:var(--muted)">A4 s QR kódem, který vede přímo na naše kočky k adopci. Stačí vytisknout.</p>
            <div class="btn-row" style="margin-bottom:1.5rem">
              <a class="btn" href="plakat.html">{ICON["print"]}Otevřít plakát</a>
            </div>
            {share("Depozitum chlup-nechlup ze Strakonic hledá domovy pro kočky z ulice. Podívej se, kdo čeká:", "index.html")}
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <p class="eyebrow">Další možnosti</p>
          <h2 class="reveal">Pomoct se dá i jinak</h2>
        </div>
        <div class="help-grid" style="grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))">
          <a class="help-card reveal" href="kocky-k-adopci.html">
            <div class="help-card__icon">{ICON["home"]}</div>
            <h3>Adopce</h3>
            <p>Nejlepší pomoc je stabilní a bezpečný domov. Adopce je bez poplatku.</p>
            <span class="help-card__more">Kočky k adopci{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.08s" href="docasna-pece.html">
            <div class="help-card__icon">{ICON["paw"]}</div>
            <h3>Dočasná péče</h3>
            <p>Dejte zdravé kočce domov, než najde ten trvalý. Náklady hradíme my.</p>
            <span class="help-card__more">Jak to funguje{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.16s" href="nasli-jste-kocku.html">
            <div class="help-card__icon">{ICON["search"]}</div>
            <h3>Hlaste nálezy obci</h3>
            <p>Každá nahlášená kočka tlačí obce k tomu, aby problém s kočkami začaly řešit.</p>
            <span class="help-card__more">Jak postupovat{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.24s" href="mailto:{EMAIL}?subject=Chci%20pom%C3%A1hat%20s%20focen%C3%ADm%20a%20sd%C3%ADlen%C3%ADm">
            <div class="help-card__icon">{ICON["camera"]}</div>
            <h3>Focení a sdílení</h3>
            <p>Dita uvítá pomoc s focením koček a se správou Facebooku. Dobrá fotka pomůže kočce k domovu nejvíc.</p>
            <span class="help-card__more">Nabídnout pomoc{ICON["arrow"]}</span>
          </a>
        </div>
      </div>
    </section>

    <section class="section section--sand section--tight">
      <div class="wrap wrap--narrow center">
        <p class="statement" data-words style="margin-inline:auto">Za patnáct let jsme zachránili stovky koček. <em>Bez vašich darů by to nešlo.</em> Děkujeme.</p>
      </div>
    </section>
"""

# ---------------------------------------------------------------------------
# Našli jste kočku?
# ---------------------------------------------------------------------------

NALEZ = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">Našli jste kočku?</p>
        <h1 class="reveal" style="--d:.06s">Co dělat, když <span class="accent-word">najdete kočku</span></h1>
        <p class="lead reveal" style="--d:.12s">Nalezené zvíře je potřeba ohlásit obci a obec se o ně musí postarat, o kočku stejně jako o psa. Postup, který opravdu pomáhá, sepsala Eva Hulcová a zveřejňujeme ho zkrácený s jejím laskavým svolením.</p>
        <div class="btn-row reveal" style="--d:.18s">
          <a class="btn btn--ghost" href="#kotata">Našli jste koťata?</a>
          <a class="btn btn--ghost" href="#ztracena">Ztratila se vám kočka?</a>
        </div>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        <h2 class="visually-hidden">Komu volat</h2>
        <div class="found-steps">
          <div class="found-step reveal"><h3>Městská policie</h3><p>Kde ji mají, volejte <a class="phone" href="tel:156">156</a></p></div>
          <div class="found-step reveal" style="--d:.08s"><h3>Starosta obce</h3><p>Kde městská policie není, volejte starostovi nebo na odbor životního prostředí.</p></div>
          <div class="found-step reveal" style="--d:.16s"><h3>Až potom útulek</h3><p>Když vás obec odmítne, ozvěte se nám na <a class="phone" href="tel:{PHONE_TEL}">{PHONE}</a>. Poradíme a pomůžeme.</p></div>
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        <div class="layout-aside">
          <div class="prose">
            <ol>
              <li><strong>Nepište nejdřív na Facebook a nevolejte hned do útulků.</strong></li>
              <li><strong>Občanský zákoník, § 1058 odst. 1:</strong> „Je-li nalezeno zvíře, u něhož je zjevné, že mělo vlastníka, oznámí nálezce nález bez zbytečného odkladu obci, nelze-li z okolností poznat, komu má být vráceno.“ Obec se pak o zvíře musí postarat, o psa stejně jako o kočku.</li>
              <li>Tam, kde je městská policie, volejte <a href="tel:156">156</a>. Kde není, volejte odbor životního prostředí, ale především si najděte číslo na starostu obce.</li>
              <li>Volat musíte starostovi nebo městské policii <strong>v místě, kde jste kočičku našli</strong>, ne do jiného města.</li>
              <li>Volejte na obec tak, jako voláte nám: ve dne, pozdě večer, o svátku i v neděli. Péče o nalezená zvířata je ze zákona úkol obce, my pomáháme dobrovolně. Nestyďte se, takhle je to správně.</li>
              <li>Do útulku volejte, až když na obci narazíte. Mnoho obcí zákony nezná. Nahrávejte hovor, stěžujte si, chtějte odmítnutí písemně. Správný útulek vám poradí, pomůže a zavolá starostovi.</li>
              <li>Každá nenahlášená kočka je pro obec „neviditelná“. Obce pak tvrdí, že problém s kočkami nemají, a celý systém se nemůže zlepšit.</li>
              <li>Pokud obec kočku přijme, sledujte její další osud. Kočka musí být obcí zaevidovaná a vyhlášená na úřední desce, aby se mohl dohledat případný majitel. Předem upozorněte, že se budete zajímat.</li>
              <li>Nedávejte kočky do pochybných útulků, které zvířata hromadí a nevydávají. Správný útulek poznáte podle toho, že má IČO, sbírkový účet, výroční zprávy, web s datem a místem nálezu koček, nehromadí zvířata, nemá extrémní úmrtnost a nalezené kočky má nahlášené obcím.</li>
            </ol>
            <blockquote>
              <p>Prosím nálezce, aby na nás brali ohled. Je nás málo a chodíme do vlastní práce. Postupujte prosím podle návodu a podle zákona právě proto, aby se podmínky pro toulavé kočky v naší zemi změnily. Moc děkuji. Sdílejte prosím.</p>
              <p style="margin:0"><strong>Eva Hulcová</strong></p>
            </blockquote>

            <h2 id="kotata">Našli jste koťata?</h2>
            <p>Malá koťata bez matky nemusí být opuštěná. Kočka je často jen na lovu a vrátí se.</p>
            <ul>
              <li><strong>Nejdřív pozorujte z dálky</strong>, klidně několik hodin. Pokud se matka vrací, nechte koťata u ní, je to pro ně nejlepší.</li>
              <li>Pro maličká koťata je větší nebezpečí <strong>chlad než hlad</strong>. Pokud jsou mokrá, studená nebo v ohrožení, zahřejte je (láhev s teplou vodou zabalená v ručníku) a hned volejte městskou policii <a href="tel:156">156</a> nebo na obecní úřad. Když nikoho nezastihnete, zavolejte nám: <a href="tel:{PHONE_TEL}">{PHONE}</a>.</li>
              <li>Nekrmte je kravským mlékem. Koťatům škodí.</li>
              <li>Postup s obcí platí i pro koťata. Matku je pak potřeba odchytit a vykastrovat, jinak bude za pár měsíců další vrh.</li>
            </ul>

            <h2 id="kastrace">Krmíte kočky na dvoře?</h2>
            <p>Nejvíc pomůžete, když je necháte vykastrovat. Jedna nevykastrovaná kočka může mít dvakrát až třikrát do roka koťata.</p>
            <ul>
              <li>Spolek <a href="https://www.feliti.cz/kastrace/" target="_blank" rel="noopener">Feliti</a> proplácí kastrace toulavých koček i lidem, kteří je krmí.</li>
              <li>Projekt <a href="https://www.obcekastruji.cz/" target="_blank" rel="noopener">Obce kastrují</a> pomáhá s kastracemi, na kterých se podílí obec, a radí, jak obec oslovit.</li>
              <li>S odchytem rádi poradíme, ozvěte se.</li>
            </ul>

            <h2 id="ztracena">Ztratila se vám kočka?</h2>
            <p>Většina ztracených koček je blíž, než si myslíte. Podle studie australských vědců byly tři čtvrtiny nalezených koček do 500 metrů od místa, kde utekly.</p>
            <ul>
              <li><strong>Hledejte hned a pěšky</strong>, hlavně za soumraku a v noci, kdy je klid. Volejte ji tichým hlasem a zachrastěte granulemi.</li>
              <li>Poproste sousedy, ať se podívají do kůlen, garáží, sklepů a altánů. Vyděšená kočka se schová a nemňouká.</li>
              <li>Nahlaste ztrátu obci a městské policii, vyvěste letáky s fotkou a zveřejněte ji na Pesweb.cz v sekci <a href="https://www.pesweb.cz/ztracene-zvire" target="_blank" rel="noopener">Ztratili jste zvíře?</a> Podívejte se i mezi <a href="kocky-k-adopci.html">naše kočky k adopci</a>.</li>
              <li>Pokud je kočka čipovaná, ověřte, že je čip zaregistrovaný na vaše aktuální údaje.</li>
            </ul>
            <div class="callout">
              <p><strong>Tip:</strong> Zkuste také službu <a href="https://najdimazlicka.cz/" target="_blank" rel="noopener">Najdi mazlíčka</a>, která hledá ztracená zvířata po celé republice pomocí kampaní na sociálních sítích.</p>
            </div>
          </div>
          <aside class="aside-card reveal" id="obec-odmitla">
            <h3>Obec odmítla?</h3>
            <p>Ozvěte se nám. Rádi poradíme, jak postupovat, a pomůžeme s jednáním s obcí.</p>
            <div class="btn-row" style="flex-direction:column">
              <a class="btn" href="tel:{PHONE_TEL}">{ICON["phone"]}{PHONE}</a>
              <a class="btn btn--ghost" href="mailto:{EMAIL}?subject=Nalezen%C3%A1%20ko%C4%8Dka">{ICON["mail"]}Napsat e-mail</a>
            </div>
            <p class="aside-card__more">Jste ze zastupitelstva obce? <a href="pro-obce.html">Spolupráce s obcemi</a></p>
          </aside>
        </div>
      </div>
    </section>
"""

# ---------------------------------------------------------------------------
# Pro obce
# ---------------------------------------------------------------------------

PROOBCE = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">Pro obce</p>
        <h1 class="reveal" style="--d:.06s">Toulavé kočky ve vaší obci? <span class="accent-word">Domluvme se.</span></h1>
        <p class="lead reveal" style="--d:.12s">Nalezená zvířata má ze zákona na starosti obec. Strakonice to od roku 2024 řeší smlouvou s naším depozitem. Rádi se pobavíme i s vámi, co by fungovalo u vás.</p>
        <div class="btn-row reveal" style="--d:.18s">
          <a class="btn" href="tel:{PHONE_TEL}">{ICON["phone"]}{PHONE}</a>
          <a class="btn btn--ghost" href="mailto:{EMAIL}?subject=Spolupr%C3%A1ce%20s%20obc%C3%AD">{ICON["mail"]}Napsat e-mail</a>
        </div>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0" aria-labelledby="obce-co">
      <div class="wrap">
        <h2 id="obce-co" class="reveal">Co s kočkami děláme</h2>
        <div class="found-steps">
          <div class="found-step reveal"><h3>Odchyt</h3><p>Odchytíme nalezené a toulavé kočky, často i celé vrhy koťat.</p></div>
          <div class="found-step reveal" style="--d:.08s"><h3>Karanténa a léčba</h3><p>Každá kočka projde karanténou a dostane veterinární péči.</p></div>
          <div class="found-step reveal" style="--d:.16s"><h3>Kastrace a domov</h3><p>Dospělé kočky odcházejí kastrované. Nový domov jim hledáme přes Pesweb.cz, adopce je bez poplatku.</p></div>
        </div>
      </div>
    </section>

    <section class="section section--sand">
      <div class="wrap">
        <div class="split split--top">
          <div class="prose">
            <p class="eyebrow">Jak to funguje ve Strakonicích</p>
            <h2 class="reveal">Smlouva a měsíční příspěvek</h2>
            <p class="reveal">Město Strakonice má s depozitem od roku 2024 smlouvu a přispívá {fmt_kc(CITY_MONTHLY)} měsíčně. To pokryje zhruba třetinu nákladů, zbytek platí dárci. Nalezené kočky ze Strakonic díky tomu mají kam jít.</p>
            <h3 class="reveal">Než zavoláte</h3>
            <p class="reveal">Depozitum má 20 míst a v sezóně koťat bývá plné. Proto se domlouváme předem a rozsah i příspěvek obce nastavujeme tak, aby to zvládly obě strany.</p>
          </div>
          <div class="prose">
            <p class="eyebrow">Co říká zákon</p>
            <h2 class="reveal">Nalezená kočka patří obci</h2>
            <p class="reveal">Nález zvířete, které zjevně mělo majitele, musí nálezce ohlásit obci (§ 1058 občanského zákoníku) a obec se o ně musí postarat, o kočku stejně jako o psa. Každá nahlášená kočka zároveň ukazuje, jak velký problém s toulavými kočkami v obci je.</p>
            <h3 class="reveal">Nejlevnější je kastrace</h3>
            <p class="reveal">Projekt <a href="https://www.obcekastruji.cz/" target="_blank" rel="noopener">Obce kastrují</a> pomáhá obcím zorganizovat kastrace toulavých koček. Spolek <a href="https://www.feliti.cz/kastrace/" target="_blank" rel="noopener">Feliti</a> proplácí kastrace i lidem, kteří kočky krmí. S odchytem rádi poradíme.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        <div class="layout-aside">
          <div class="prose">
            <h2 class="reveal">Co můžete udělat hned</h2>
            <ul class="reveal">
              <li>Dejte na web obce a do zpravodaje, komu mají lidé nalezenou kočku hlásit.</li>
              <li>Pověste na obecní nástěnku náš <a href="plakat.html">plakát s kočkami k adopci</a>.</li>
              <li>Zavolejte nám, když se ve vaší obci objeví kočky s koťaty. Čím dřív, tím menší kolonie.</li>
            </ul>
          </div>
          <aside class="aside-card reveal">
            <h3>Kontakt</h3>
            <p>Dita Uhriková, předsedkyně spolku {ORG_NAME}, IČO {ORG_ICO}.</p>
            <div class="btn-row" style="flex-direction:column">
              <a class="btn" href="tel:{PHONE_TEL}">{ICON["phone"]}{PHONE}</a>
              <a class="btn btn--ghost" href="mailto:{EMAIL}?subject=Spolupr%C3%A1ce%20s%20obc%C3%AD">{ICON["mail"]}{EMAIL}</a>
            </div>
          </aside>
        </div>
      </div>
    </section>
"""


# ---------------------------------------------------------------------------
# O nás
# ---------------------------------------------------------------------------

ONAS = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">O nás</p>
        <h1 class="reveal" style="--d:.06s">Malé depozitum s <span class="accent-word">velkým srdcem</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Depozitum chlup-nechlup je domácí depozitum pro odchyt a léčbu koček ze Strakonic a okolí. Od roku 2023 je to zapsaný spolek ({ORG_NAME}).</p>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        <div class="split">
          <div class="split__media" data-progress><img sizes="(max-width: 860px) 92vw, 540px" src="assets/img/mourek.jpg" alt="Mourovatá kočka odpočívá na huňaté dece" fetchpriority="high"></div>
          <div class="prose">
            <h2 class="mt-0">Jak to celé začalo</h2>
            <p>Depozitum vzniklo zhruba před patnácti lety jako malé rodinné zázemí pro nalezené kočičky z okolí. Postupně se rozrostlo do dnešní velikosti.</p>
            <p>Kapacita depozita je <strong>20 míst</strong>. Část z nich zabírají kočky v karanténě a starší kočky, pro které se domov hledá těžko. Kvůli nemocem navíc ubytováváme kočky z různých lokalit odděleně a důsledně dodržujeme hygienu.</p>
            <p>Za rok projde depozitem <strong>téměř 200 koček</strong>. Přes Pesweb.cz už u nás domov našlo <strong>{ADOPTED} koček</strong>.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--sand">
      <div class="wrap wrap--narrow">
        <p class="statement" data-words>Kočky často čekají u nálezců nebo přímo na ulici. Jakmile se v depozitu uvolní místo, <em>čeká na něj už několik dalších</em>.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="layout-aside">
          <div class="prose">
            <h2 class="mt-0">Dita Uhriková</h2>
            <p>Depozitum založila a vede Dita Uhriková, předsedkyně spolku. Kočky odchytává, léčí a hledá jim domov už patnáct let. Hotovo pořád není: na ulicích se objevují další kočky i s koťaty.</p>
            <p>Rozhovor s Ditou si můžete přečíst na portálu <a href="https://www.jcted.cz/dita-uhrikova-bojuje-za-kocici-utulek-za-obce-hasime-problemy-z-urazek-na-internetu-si-nic-nedelam-rika/" target="_blank" rel="noopener">Jižní Čechy Teď</a>.</p>

            <h2>Strakonice nemají vlastní kočičí útulek</h2>
            <p>Dlouhá léta jsme všechno platili jen z darů. Od roku 2024 máme smlouvu s Městem Strakonice, které nám přispívá {fmt_kc(CITY_MONTHLY)} měsíčně. Příspěvek pokryje zhruba třetinu nákladů, zbytek dávají dárci.</p>
            <p>Zvlášť v době jarních koťat se snažíme depozitum „nafouknout“ a využít každou dočasnou péči, kterou najdeme. Kapacitou ale nemůžeme pokrýt péči o všechny nechtěné a toulavé kočky ze Strakonic a přilehlých obcí. Obcím, které to chtějí řešit, rádi poradíme: <a href="pro-obce.html">spolupráce s obcemi</a>.</p>

            <h2>Kdo nám pomáhá</h2>
            <p>Velkou pomocí jsou organizace jako <a href="https://www.feliti.cz/" target="_blank" rel="noopener">Feliti</a>, které proplácejí kastrace koček i „běžným smrtelníkům“, nebo spolek <a href="https://www.pomahejmezviratum.cz/" target="_blank" rel="noopener">Pomáhejme zvířatům</a>. Podporujeme také projekt <a href="https://www.obcekastruji.cz/" target="_blank" rel="noopener">Obce kastrují</a>, který šíří osvětu o nutnosti kastrace koček.</p>
            <div class="callout"><p><strong>Kastrovat, kastrovat, kastrovat.</strong> Místo aby koček za ta léta ubývalo, spíš přibývají. Jediná cesta ven je důsledná kastrace, i u koček „na dvoře“.</p></div>

            <h2>Údaje o spolku</h2>
            <p><strong>{ORG_NAME}</strong><br>IČO {ORG_ICO}<br>Sídlo: {ORG_SEAT} (návštěvy jen po domluvě)<br>{ORG_REG[0].upper() + ORG_REG[1:]}<br>Předsedkyně spolku: Dita Uhriková<br>Transparentní účet: {ACCOUNT} (Fio banka)</p>
            <p><a href="{JUSTICE_DOCS}" target="_blank" rel="noopener">Účetní závěrky a stanovy</a> najdete ve sbírce listin na justice.cz.</p>
          </div>
          <aside class="aside-card reveal">
            <h3>Sledujte nás</h3>
            <p>Nejnovější informace najdete na Facebooku Depozita, nejčerstvější zprávy pak na Ditině osobním profilu.</p>
            <div class="btn-row" style="flex-direction:column">
              <a class="btn" href="{FB}" target="_blank" rel="noopener">{ICON["fb"]}Facebook Depozita</a>
              <a class="btn btn--ghost" href="{IG}" target="_blank" rel="noopener">{ICON["ig"]}Instagram</a>
              <a class="btn btn--ghost" href="{FB_DITA}" target="_blank" rel="noopener">Profil Dity Uhrikové</a>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        {cta_band("Chcete nám pomoct?", "Adopcí, dočasnou péčí, darem nebo jen sdílením. Každá pomoc se počítá.", "podporte-nas.html", "Jak pomoct")}
      </div>
    </section>
"""

# ---------------------------------------------------------------------------
# Plakát k vytištění
# ---------------------------------------------------------------------------

PLAKAT = f"""
    <section class="page-hero no-print">
      <div class="wrap">
        <p class="eyebrow">Plakát k vytištění</p>
        <h1>Pověste plakát tam, kde ho lidé uvidí.</h1>
        <p class="lead">U veterináře, v obchodě, na obecní nástěnce nebo v práci. QR kód vede přímo na naše kočky k adopci na webu.</p>
        <div class="btn-row"><button class="btn" type="button" onclick="window.print()">{ICON["print"]}Vytisknout plakát</button></div>
      </div>
    </section>

    <section class="section section--tight poster-wrap" style="padding-top:0">
      <div class="wrap">
        <article class="poster">
          <div class="poster__photos">
            <img src="assets/img/domov/ludvik-lucian.jpg" alt="" data-noopt>
            <img src="assets/img/domov/bozanek.jpg" alt="" data-noopt>
            <img src="assets/img/domov/xia.jpg" alt="" data-noopt>
          </div>
          <p class="poster__caption">Na fotkách Ludvík a Lucián, Božánek a Xia. Ti už domov mají, teď čekají další.</p>
          <p class="poster__eyebrow">Depozitum chlup-nechlup · Strakonice</p>
          <h2 class="poster__title">Hledáme domov<br>pro kočky z ulice</h2>
          <p class="poster__lead">Desítky koček a koťat z okolí Strakonic čekají na svého člověka. Jsou ošetřené, dospělé kočky kastrované. <strong>Adopce je bez poplatku.</strong></p>
          <div class="poster__bottom">
            <div class="poster__qr"><img src="assets/img/qr-adopce.svg" alt="QR kód na kočky k adopci"></div>
            <div>
              <p class="poster__big">Naskenujte a vyberte si</p>
              <p class="poster__url">{SITE_URL.replace("https://", "").rstrip("/")}</p>
              <p class="poster__phone">{ICON["phone"]}{PHONE}</p>
              <p>Hledáme i dočasné domovy a dárce. Transparentní účet {ACCOUNT}</p>
            </div>
          </div>
        </article>
      </div>
    </section>
"""

SOUKROMI = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">Soukromí a cookies</p>
        <h1 class="reveal" style="--d:.06s">Jak web zachází s vašimi údaji</h1>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        <div class="prose">
          <h2 class="mt-0">Kdo web provozuje</h2>
          <p>{ORG_NAME}, IČO {ORG_ICO}, sídlo {ORG_SEAT}. Kontakt: <a href="mailto:{EMAIL}">{EMAIL}</a>, {PHONE}.</p>

          <h2>Cookies</h2>
          <p>Tento web sám žádné cookies neukládá a nepoužívá žádnou analytiku ani reklamní nástroje. Písma jsou uložená přímo na webu, takže se nenačítají od Googlu.</p>
          <p>Seznam koček k adopci zobrazujeme pomocí widgetu portálu <a href="https://www.pesweb.cz/" target="_blank" rel="noopener">Pesweb.cz</a>. Widget se načítá z jeho serverů, až když se k němu posunete. Pesweb v něm používá ochranu Cloudflare (technická cookie <code>cf_clearance</code>) a načítá i služby Googlu (písma, Tag Manager, reklamní a souhlasové skripty); o případný souhlas s cookies vás požádá sám. Údaje, které widget sbírá, zpracovává Pesweb.cz podle svých zásad. Odkazy na Facebook, Instagram a WhatsApp jsou obyčejné odkazy; data se těmto službám předají, až když na odkaz kliknete.</p>

          <h2>Osobní údaje</h2>
          <p>Dotazníky na webu (adopce, dočasná péče) nic neukládají ani nikam neodesílají: jen z vašich odpovědí připraví zprávu, kterou sami pošlete e-mailem nebo SMS. Když nám napíšete nebo zavoláte kvůli adopci, dočasné péči, nálezu kočky nebo potvrzení o daru, použijeme vaše údaje jen k vyřízení vaší žádosti, k uzavření adopční smlouvy a k vystavení potvrzení o daru, a uchováme je jen po dobu nutnou podle zákona.</p>
          <p>Fotky koček od nových majitelů zveřejníme jen s jejich souhlasem. Máte právo na přístup ke svým údajům, jejich opravu a výmaz; stačí napsat na <a href="mailto:{EMAIL}">{EMAIL}</a>. Stížnost můžete podat u Úřadu pro ochranu osobních údajů.</p>
        </div>
      </div>
    </section>
"""

POSTER_CSS = """
  <style>
    .poster { max-width: 794px; margin: 0 auto; aspect-ratio: 210 / 297; background: #fffaf2; color: #2b211b; border-radius: 24px; box-shadow: var(--shadow); padding: 48px; display: flex; flex-direction: column; overflow: hidden; }
    .poster__photos { display: grid; grid-template-columns: 1.3fr 1fr 1fr; gap: 10px; height: 34%; margin-bottom: 28px; }
    .poster__photos img { width: 100%; height: 100%; object-fit: cover; border-radius: 18px; }
    .poster__eyebrow { font-weight: 800; letter-spacing: .14em; text-transform: uppercase; font-size: .8rem; color: #a8441a; margin: 0 0 10px; }
    .poster__title { font-size: clamp(2rem, 6vw, 3.6rem); margin: 0 0 16px; color: #2b211b; }
    .poster__lead { font-size: 1.15rem; margin: 0 0 auto; color: #5d4f45; }
    .poster__bottom { display: grid; grid-template-columns: 170px 1fr; gap: 24px; align-items: center; border-top: 2px dashed rgba(43,33,27,.2); padding-top: 24px; margin-top: 24px; }
    .poster__qr { background: #fff; padding: 8px; border-radius: 12px; }
    .poster__qr img { width: 100%; height: auto; }
    .poster__big { font-family: var(--font-display); font-size: 1.6rem; font-weight: 600; margin: 0 0 4px; }
    .poster__bottom p { margin: 0 0 6px; }
    .poster__phone { display: flex; align-items: center; gap: 8px; font-family: var(--font-display); font-weight: 700; font-size: 1.7rem; color: #a8441a; }
    .poster__phone svg { width: 26px; height: 26px; }
    @media (max-width: 600px) { .poster { padding: 22px; aspect-ratio: auto; } .poster__bottom { grid-template-columns: 110px 1fr; } .poster__phone { font-size: 1.25rem; } }
    @media print {
      @page { size: A4; margin: 0; }
      body { background: #fff; }
      .site-header, .site-footer, .progress, .skip-link, .no-print { display: none !important; }
      .poster-wrap { padding: 0 !important; }
      .poster-wrap .wrap { padding: 0; max-width: none; }
      .poster { box-shadow: none; border-radius: 0; width: 210mm; height: 297mm; max-width: none; aspect-ratio: auto; padding: 16mm; }
      .poster__phone { font-size: 2.2rem; }
      .poster__title { font-size: 3.6rem; }
      .poster__lead { font-size: 1.4rem; }
    }
  </style>"""

NOT_FOUND = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow">Chyba 404</p>
        <h1>Tahle stránka <span class="accent-word">utekla</span>.</h1>
        <p class="lead">Možná se schovala pod gauč, možná nikdy neexistovala. Zkuste začít znovu od úvodu, nebo se rovnou podívejte, kdo hledá domov.</p>
        <div class="btn-row">
          <a class="btn" href="{SITE_URL}">Na úvod{ICON["arrow"]}</a>
          <a class="btn btn--ghost" href="{SITE_URL}kocky-k-adopci.html">Kočky k adopci</a>
        </div>
      </div>
    </section>
"""

MANIFEST = json.dumps({
    "name": "Depozitum chlup-nechlup",
    "short_name": "chlup-nechlup",
    "description": "Kočky z ulice ze Strakonic a okolí hledají domov.",
    "lang": "cs",
    "start_url": "./",
    "display": "standalone",
    "background_color": "#f7f0e5",
    "theme_color": "#b94f1b",
    "icons": [
        {"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
    ],
}, ensure_ascii=False, indent=2)

SITEMAP_PAGES = ["", "kocky-k-adopci.html", "nasli-domov.html", "docasna-pece.html", "podporte-nas.html", "nasli-jste-kocku.html", "pro-obce.html", "o-nas.html", "plakat.html", "soukromi.html"]

FAVICON = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="14" fill="#d4612a"/><g fill="#fffaf2" transform="translate(6 6) scale(.75)">{PAW_PATHS}</g></svg>'

if __name__ == "__main__":
    (OUT / "assets/img/favicon.svg").write_text(FAVICON, encoding="utf-8")
    make_qr()
    page("index.html", "Depozitum chlup-nechlup · Kočky k adopci Strakonice", "Domácí depozitum pro odchyt, léčbu a kastraci koček ze Strakonic a okolí. Kočky k adopci bez poplatku, dočasná péče a transparentní účet.", INDEX,
         f'\n  <script type="application/ld+json">{JSONLD}</script>')
    page("kocky-k-adopci.html", "Kočky k adopci", "Kočky ze Strakonic a okolí, které hledají stabilní a bezpečný domov. Adopce bez poplatku, jak probíhá a na co se připravit.", ADOPCE)
    page("nasli-domov.html", "Domov našli", f"Už {ADOPTED} koček z Depozita chlup-nechlup ve Strakonicích našlo nový domov. Podívejte se na šťastné konce i na kočky, které ještě čekají.", NASLI)
    page("docasna-pece.html", "Dočasná péče", "Dočasná péče o kočky ze Strakonic: náklady hradí depozitum, vy dáte kočce domov na přechodnou dobu.", DOCASKA)
    page("podporte-nas.html", "Podpořte nás", "Transparentní účet 6077760777/2010, QR platba, trvalý příkaz, věcné dary a sdílení. Jak podpořit Depozitum chlup-nechlup.", PODPORA)
    page("nasli-jste-kocku.html", "Našli jste kočku?", "Co dělat, když najdete toulavou kočku nebo koťata, a jak hledat ztracenou kočku.", NALEZ)
    page("pro-obce.html", "Pro obce", "Toulavé kočky v obci: co dělá Depozitum chlup-nechlup, jak spolupracuje se Strakonicemi a jak se domluvit na spolupráci.", PROOBCE)
    page("o-nas.html", "O nás", "Příběh Depozita chlup-nechlup ze Strakonic a jeho zakladatelky Dity Uhrikové. Kdo nám pomáhá, proč kastrovat a údaje o spolku.", ONAS)
    page("plakat.html", "Plakát k vytištění", "Plakát A4 k vytištění s QR kódem na kočky k adopci z Depozita chlup-nechlup. Pověste ho u veterináře, v obchodě nebo na obci.", PLAKAT, POSTER_CSS)
    page("404.html", "Stránka nenalezena", "Tahle stránka na webu Depozita chlup-nechlup neexistuje. Zkuste úvod nebo kočky k adopci.", NOT_FOUND)
    (OUT / "manifest.webmanifest").write_text(MANIFEST + "\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    host = urlparse(SITE_URL).hostname
    cname = OUT / "CNAME"
    if host.endswith(".github.io"):
        cname.unlink(missing_ok=True)
    else:
        cname.write_text(host + "\n", encoding="utf-8")
    urls = "\n".join(f"  <url><loc>{SITE_URL}{u}</loc></url>" for u in SITEMAP_PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf-8")
    page("soukromi.html", "Soukromí a cookies", "Jak web Depozita chlup-nechlup zachází s osobními údaji a cookies, co načítá widget Pesweb.cz a jaká máte práva.", SOUKROMI)
