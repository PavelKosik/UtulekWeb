#!/usr/bin/env python3
"""Sestaví statické HTML stránky webu Depozitum chlup-nechlup do repozitáře."""
import pathlib
import sys

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent

PHONE = "+420 607 707 537"
PHONE_TEL = "+420607707537"
EMAIL = "ditau@email.cz"
ACCOUNT = "6077760777/2010"
FIO = "https://ib.fio.cz/ib/transparent?a=6077760777"
FB = "https://www.facebook.com/depozitumchlupnechlup"
FB_DITA = "https://www.facebook.com/dita.uhrikova/"
IG = "https://www.instagram.com/chlupnechlup/"
PESWEB = "https://www.pesweb.cz/cz/depozitum-chlup-nechlup"

ICON = {
    "paw": '<svg viewBox="0 0 48 48" aria-hidden="true" fill="currentColor"><ellipse cx="11" cy="20" rx="4.6" ry="6" transform="rotate(-18 11 20)"/><ellipse cx="19.5" cy="11.5" rx="4.8" ry="6.4" transform="rotate(-6 19.5 11.5)"/><ellipse cx="29.5" cy="11.5" rx="4.8" ry="6.4" transform="rotate(6 29.5 11.5)"/><ellipse cx="38" cy="20" rx="4.6" ry="6" transform="rotate(18 38 20)"/><path d="M24.5 22c-6.2 0-12.5 8.6-12.5 13.6 0 4 3.2 5.9 6.6 5.9 2.6 0 4-1.3 5.9-1.3s3.3 1.3 5.9 1.3c3.4 0 6.6-1.9 6.6-5.9C37 30.6 30.7 22 24.5 22z"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20.5s-7.5-4.4-9.3-9.6C1.5 7.4 3.8 4 7.3 4c2 0 3.6 1.1 4.7 2.7C13.1 5.1 14.7 4 16.7 4c3.5 0 5.8 3.4 4.6 6.9-1.8 5.2-9.3 9.6-9.3 9.6z"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 9.5V20h14V9.5"/><path d="M10 20v-5h4v5"/></svg>',
    "coin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="6" width="19" height="13" rx="2.5"/><path d="M2.5 10.5h19M6.5 15h3"/></svg>',
    "share": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>',
    "copy": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2.5"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>',
    "external": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 3h3.5l2 5-2.5 1.5a11 11 0 0 0 6.5 6.5L16 13.5l5 2V19a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.6-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.2H7.9v3h2.6V21h3z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="1" fill="currentColor" stroke="none"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>',
}

NAV = [
    ("kocky-k-adopci.html", "Kočky k adopci"),
    ("nasli-domov.html", "Domov našli"),
    ("docasna-pece.html", "Dočasná péče"),
    ("nasli-jste-kocku.html", "Našli jste kočku?"),
    ("o-nas.html", "O nás"),
]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&amp;'
    'family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,500..700,100,0..1;1,9..144,500..700,100,0..1&amp;display=swap" rel="stylesheet">'
)


def head(title, desc, current):
    full = title if current == "index.html" else f"{title} · Depozitum chlup-nechlup"
    return f"""<!doctype html>
<html lang="cs" class="js-off">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{full}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#f7f0e5">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:site_name" content="Depozitum chlup-nechlup">
  <meta property="og:title" content="{full}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="assets/img/kocka-tuxedo.jpg">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  {FONTS}
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  <a class="skip-link" href="#obsah">Přeskočit na obsah</a>
  <div class="progress" aria-hidden="true"></div>
{header(current)}
  <main id="obsah">
"""


def header(current):
    links = "\n".join(
        f'        <a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
        for href, label in NAV
    )
    return f"""  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="index.html" aria-label="Depozitum chlup-nechlup — úvod">
        {ICON["paw"]}
        <span>chlup-nechlup<small>Depozitum pro kočky · Strakonice</small></span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="hlavni-menu" aria-label="Menu"><span></span></button>
      <nav class="nav" id="hlavni-menu" aria-label="Hlavní menu">
{links}
        <a class="btn" href="podporte-nas.html"{" aria-current=\"page\"" if current == "podporte-nas.html" else ""}>{ICON["heart"]}Podpořit</a>
      </nav>
    </div>
  </header>"""


def footer():
    nav = "\n".join(f'            <li><a href="{h}">{l}</a></li>' for h, l in NAV)
    return f"""  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div>
          <p class="footer-big">Každá kočka si zaslouží teplé místo.</p>
          <p style="opacity:.8;max-width:38ch">Domácí soukromé depozitum pro odchyt a léčbu koček ze Strakonic a okolí. Fungujeme jen díky vašim darům.</p>
          <div class="socials">
            <a href="{FB}" target="_blank" rel="noopener" aria-label="Facebook Depozita">{ICON["fb"]}</a>
            <a href="{IG}" target="_blank" rel="noopener" aria-label="Instagram">{ICON["ig"]}</a>
            <a href="mailto:{EMAIL}" aria-label="E-mail">{ICON["mail"]}</a>
          </div>
        </div>
        <div>
          <h4>Web</h4>
          <ul>
            <li><a href="index.html">Úvod</a></li>
{nav}
            <li><a href="podporte-nas.html">Podpořte nás</a></li>
          </ul>
        </div>
        <div>
          <h4>Kontakt</h4>
          <ul>
            <li>Depozitum chlup-nechlup</li>
            <li>Strakonice</li>
            <li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
            <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          </ul>
        </div>
        <div>
          <h4>Transparentní účet</h4>
          <ul>
            <li><strong>{ACCOUNT}</strong></li>
            <li>Fio banka</li>
            <li><a href="{FIO}" target="_blank" rel="noopener">Pohyby na účtu</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© <span data-year>2026</span> Depozitum chlup-nechlup</span>
        <span>Kočky k adopci zveřejňujeme přes <a href="{PESWEB}" target="_blank" rel="noopener">Pesweb.cz</a></span>
      </div>
    </div>
  </footer>

  <script src="assets/js/main.js"></script>
</body>
</html>
"""


def widget(container, filters, layout=None):
    """Vloží widget Pesweb.cz se seznamem koček, barevně sladěný s webem."""
    import json
    cfg = {
        "container": f"#{container}",
        "baseUrl": "https://www.pesweb.cz",
        "type": "cat",
        "filters": filters,
        "height": "auto",
        "theme": {"primaryColor": "#d4612a", "backgroundColor": "#fffaf2", "textColor": "#2b211b", "borderRadius": "16px"},
    }
    if layout:
        cfg["layout"] = layout
    return f"""<div class="widget-shell reveal">
          <div id="{container}">
            <p class="widget-fallback">Načítáme kočičky… Pokud se seznam nezobrazí, najdete je přímo na <a href="{PESWEB}" target="_blank" rel="noopener">Pesweb.cz</a>.</p>
          </div>
        </div>
        <p class="widget-note">Seznam se nenačetl? <a href="{PESWEB}" target="_blank" rel="noopener">Otevřete naše kočky na Pesweb.cz</a></p>
        <script src="https://www.pesweb.cz/widget/pesweb-widget.min.js"></script>
        <script>
          if (window.PeswebWidget) PeswebWidget.init({json.dumps(cfg, ensure_ascii=False)});
        </script>"""


def account_card(extra_class=""):
    return f"""<div class="account {extra_class}" data-progress>
          <div>
            <div class="account__label">Transparentní účet · Fio banka</div>
            <div class="account__number">{ACCOUNT}</div>
            <div class="account__meta">Depozitum chlup-nechlup · IBAN CZ61 2010 0000 0060 7776 0777</div>
            <div class="btn-row">
              <button class="btn" type="button" data-copy="{ACCOUNT}">{ICON["copy"]}<span>Kopírovat číslo</span></button>
              <a class="btn btn--ghost" href="{FIO}" target="_blank" rel="noopener">Pohyby na účtu{ICON["external"]}</a>
            </div>
          </div>
          <div class="account__qr">
            <img src="assets/img/qr-platba.svg" alt="QR platba na transparentní účet {ACCOUNT}" width="130" height="130">
            QR platba — částku zadáte v aplikaci banky
          </div>
        </div>"""


def cta_band(title, text, href, label):
    return f"""<div class="cta-band reveal" data-progress>
          <div>
            <h2>{title}</h2>
            <p>{text}</p>
          </div>
          <a class="btn" href="{href}">{label}{ICON["arrow"]}</a>
          <svg class="paw-bg" viewBox="0 0 48 48" fill="currentColor" aria-hidden="true">{ICON["paw"][ICON["paw"].index(">") + 1:-6]}</svg>
        </div>"""


def page(name, title, desc, body):
    html = head(title, desc, name) + body + footer()
    (OUT / name).write_text(html, encoding="utf-8")
    print("wrote", name, len(html))


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
            <a class="btn btn--ghost" href="#pomoc">Jak můžu pomoct</a>
          </div>
        </div>
        <div class="collage reveal reveal--scale" style="--d:.1s" aria-hidden="true">
          <figure class="c1"><img src="assets/img/kocka-tuxedo.jpg" alt="" width="959" height="652" fetchpriority="high"></figure>
          <figure class="c2"><img src="assets/img/xantipa.jpg" alt="" width="527" height="938"></figure>
          <figure class="c3"><img src="assets/img/eliot-a-emil.jpg" alt="" width="960" height="720"></figure>
          <div class="sticker"><span><strong>100+</strong>koček ročně projde depozitem</span></div>
        </div>
      </div>
      <a class="scroll-cue" href="#pribeh"><i></i>Scrollujte</a>
    </section>

    <section class="section section--tight" id="pribeh">
      <div class="wrap">
        <p class="eyebrow">Kdo jsme</p>
        <p class="statement" data-words>Jsme malé domácí depozitum, ne městský útulek. Nikdo nás nezřizuje ani nefinancuje — <em>každou kastraci a každé ošetření</em> platíme z vašich darů.</p>
        <div class="stats">
          <div class="stat reveal"><div class="stat__num" data-count="10" data-suffix="+">10+</div><div class="stat__label">let pomáháme kočkám v nouzi</div></div>
          <div class="stat reveal" style="--d:.08s"><div class="stat__num" data-count="20">20</div><div class="stat__label">míst v depozitu, rozdělených podle místa nálezu</div></div>
          <div class="stat reveal" style="--d:.16s"><div class="stat__num" data-count="120">120</div><div class="stat__label">koček se u nás ročně vystřídá</div></div>
          <div class="stat reveal" style="--d:.24s"><div class="stat__num" data-count="0" data-suffix=" Kč">0 Kč</div><div class="stat__label">dostáváme od města nebo státu</div></div>
        </div>
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
            <img src="assets/img/odchyt.jpg" alt="" class="is-active" loading="lazy">
            <img src="assets/img/kocka-cerna.jpg" alt="" loading="lazy">
            <img src="assets/img/cassie.jpg" alt="" loading="lazy">
            <img src="assets/img/eliot-a-emil.jpg" alt="" loading="lazy">
            <img src="assets/img/kote-choi.jpg" alt="" loading="lazy">
            <div class="journey__meter"><span></span><span></span><span></span><span></span><span></span></div>
          </div>
          <ol class="journey__steps">
            <li class="journey__step is-active" data-label="Odchyt">
              <img class="mobile-img" src="assets/img/odchyt.jpg" alt="Kočka v přepravce po odchytu" loading="lazy">
              <h3>Odchyt</h3>
              <p>Sbíráme celé vrhy, dohledáváme a po nocích naháníme kočky, které se ocitly na ulici. Často čekají u nálezců nebo tam, kam je chodí krmit ohleduplní lidé.</p>
            </li>
            <li class="journey__step" data-label="Karanténa a léčba">
              <img class="mobile-img" src="assets/img/kocka-cerna.jpg" alt="Černá kočka v karanténní kleci" loading="lazy">
              <h3>Karanténa a léčba</h3>
              <p>Každá kočka projde karanténou. Kočky z různých lokalit ubytováváme odděleně a přísně dbáme na hygienu, aby se nemoci nepřenášely.</p>
            </li>
            <li class="journey__step" data-label="Kastrace">
              <img class="mobile-img" src="assets/img/cassie.jpg" alt="Želvovinová kočka Cassie" loading="lazy">
              <h3>Kastrace</h3>
              <p>Bez kastrace se kruh nezastaví. Dospělé kočky od nás odcházejí kastrované, u koťat je kastrace v dospělosti podmínkou adopce.</p>
            </li>
            <li class="journey__step" data-label="Dočasná péče">
              <img class="mobile-img" src="assets/img/eliot-a-emil.jpg" alt="Koťata Eliot a Emil" loading="lazy">
              <h3>Dočasná péče</h3>
              <p>Zdravé kočky se stěhují do domácích depozit. Tam se mazlí, zvykají si na lidi a my je díky tomu líp poznáme.</p>
            </li>
            <li class="journey__step" data-label="Nový domov">
              <img class="mobile-img" src="assets/img/kote-choi.jpg" alt="Kotě Choi v novém domově" loading="lazy">
              <h3>Nový domov</h3>
              <p>Hledáme pro každou kočku spřízněnou duši: stabilní a bezpečný domov na adopční smlouvu. A uvolněné místo hned obsadí další kočka z ulice.</p>
              <div class="btn-row"><a class="btn" href="kocky-k-adopci.html">Kdo hledá domov{ICON["arrow"]}</a></div>
            </li>
          </ol>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="adopce-nadpis">
      <div class="wrap">
        <div class="section-head">
          <p class="eyebrow">Hledají domov</p>
          <h2 id="adopce-nadpis" class="reveal">Možná na vás čeká právě teď.</h2>
          <p class="lead reveal" style="--d:.08s">Aktuální seznam koček k adopci se načítá přímo z portálu Pesweb.cz. Zaujala vás některá? Ozvěte se Ditě a domluvíte se na seznámení.</p>
        </div>
        {widget("pesweb-uvod", {"shelter": "depozitum-chlup-nechlup"}, {"itemsPerPage": 6})}
        <div class="btn-row" style="margin-top:28px">
          <a class="btn" href="kocky-k-adopci.html">Všechny kočky a podmínky adopce{ICON["arrow"]}</a>
          <a class="btn btn--ghost" href="nasli-domov.html">Kdo už domov našel</a>
        </div>
      </div>
    </section>

    <div class="marquee" data-marquee aria-hidden="true">
      <div class="marquee__track">
        <div class="marquee__item"><img src="assets/img/falca.jpg" alt="" loading="lazy"></div>
        <div class="marquee__item"><img src="assets/img/kote-choi-2.jpg" alt="" loading="lazy"></div>
        <div class="marquee__item"><img src="assets/img/mourek.jpg" alt="" loading="lazy"></div>
        <div class="marquee__item"><img src="assets/img/xantipa.jpg" alt="" loading="lazy"></div>
        <div class="marquee__item"><img src="assets/img/cassie.jpg" alt="" loading="lazy"></div>
        <div class="marquee__item"><img src="assets/img/kocka-tuxedo.jpg" alt="" loading="lazy"></div>
        <div class="marquee__item"><img src="assets/img/eliot-a-emil.jpg" alt="" loading="lazy"></div>
        <div class="marquee__item"><img src="assets/img/kocka-cerna.jpg" alt="" loading="lazy"></div>
      </div>
    </div>

    <section class="section" id="pomoc" aria-labelledby="pomoc-nadpis">
      <div class="wrap">
        <div class="section-head section-head--center">
          <p class="eyebrow">Pomáhejte s námi</p>
          <h2 id="pomoc-nadpis" class="reveal">Pomoct se dá i bez kočky doma.</h2>
          <p class="lead reveal" style="--d:.08s">Každá z těchhle věcí uvolní místo pro další kočku, která zrovna čeká venku.</p>
        </div>
        <div class="help-grid">
          <a class="help-card reveal" href="kocky-k-adopci.html">
            <div class="help-card__icon">{ICON["home"]}</div>
            <h3>Adoptujte</h3>
            <p>Dejte kočce stabilní a bezpečný domov. Pomůžeme vám vybrat tu, která sedne k vaší domácnosti.</p>
            <span class="help-card__more">Kočky k adopci{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.08s" href="docasna-pece.html">
            <div class="help-card__icon">{ICON["paw"]}</div>
            <h3>Dočasná péče</h3>
            <p>Vezměte si domů zdravou kočku, než najde nový domov. Krmení, stelivo i veterinu hradí depozitum.</p>
            <span class="help-card__more">Jak funguje dočaska{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.16s" href="podporte-nas.html">
            <div class="help-card__icon">{ICON["coin"]}</div>
            <h3>Přispějte</h3>
            <p>Kastrace, léky, krmení. Bez pravidelných dárců by depozitum nemohlo fungovat. Účet je transparentní.</p>
            <span class="help-card__more">Transparentní účet{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.24s" href="{FB}" target="_blank" rel="noopener">
            <div class="help-card__icon">{ICON["share"]}</div>
            <h3>Sdílejte</h3>
            <p>Sdílejte kočičky na Facebooku, Annonce nebo Bazoši. Nabídněte inzerci na webu obce či veterináře.</p>
            <span class="help-card__more">Facebook Depozita{ICON["arrow"]}</span>
          </a>
        </div>
      </div>
    </section>

    <section class="section section--dark" id="dar" aria-labelledby="dar-nadpis">
      <div class="wrap">
        <div class="donate">
          <div>
            <p class="eyebrow">Finanční dar</p>
            <h2 id="dar-nadpis" class="reveal">Každá koruna jde na kočky. A je to vidět.</h2>
            <p class="lead reveal" style="--d:.08s">Spravujeme transparentní účet u Fio banky, takže každý pohyb si můžete zkontrolovat. Účtenky a faktury z nákupů navíc sdílíme na Facebooku.</p>
            <a class="btn btn--light reveal" style="--d:.16s" href="podporte-nas.html">Další způsoby podpory{ICON["arrow"]}</a>
          </div>
          {account_card("reveal")}
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="nalez-nadpis">
      <div class="wrap">
        <div class="split split--top">
          <div>
            <p class="eyebrow">Našli jste kočku?</p>
            <h2 id="nalez-nadpis" class="reveal">Nejdřív volejte obec. Ze zákona.</h2>
            <p class="lead reveal" style="--d:.08s">Obec má povinnost postarat se o toulavé zvíře, o kočku stejně jako o psa (§ 1058 občanského zákoníku). Každá nenahlášená kočka znamená, že obec „problém s kočkami nemá“.</p>
            <a class="btn btn--ghost reveal" style="--d:.16s" href="nasli-jste-kocku.html">Celý postup krok za krokem{ICON["arrow"]}</a>
          </div>
          <div class="found-steps" style="grid-template-columns:1fr">
            <div class="found-step reveal"><h3>Městská policie</h3><p>Kde ji mají, volejte <a href="tel:156"><strong>156</strong></a>. Vždy na místě nálezu, ne do jiného města.</p></div>
            <div class="found-step reveal" style="--d:.08s"><h3>Starosta nebo odbor životního prostředí</h3><p>Kde městská policie není, najděte si číslo na starostu obce. Klidně večer nebo v neděli.</p></div>
            <div class="found-step reveal" style="--d:.16s"><h3>Teprve potom útulek</h3><p>Když obec odmítne, ozvěte se nám. Poradíme a pomůžeme s jednáním s obcí.</p></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--sand" aria-labelledby="dita-nadpis">
      <div class="wrap">
        <div class="split">
          <div class="split__media reveal" data-progress><img src="assets/img/kocka-tuxedo.jpg" alt="Černobílá kočka odpočívá na dece v depozitu" loading="lazy"></div>
          <div>
            <p class="eyebrow">Srdce depozita</p>
            <h2 id="dita-nadpis" class="reveal">Za vším stojí Dita.</h2>
            <p class="reveal" style="--d:.06s">Depozitum vzniklo jako malé rodinné zázemí pro nalezené kočičky z okolí. Zakladatelkou, organizátorkou, páteří a hlavně srdcem celého depozita je <strong>Dita Uhriková</strong>, která už přes deset let vytrvale bojuje s kočičími nemocemi, zraněními i s tím, že Strakonice stále nemají kočičí útulek.</p>
            <p class="reveal" style="--d:.12s">Pokud se rozhodnete kočku adoptovat, nebo jste nějakou našli, budete jednat právě s ní.</p>
            <div class="btn-row reveal" style="--d:.18s">
              <a class="btn" href="o-nas.html">Náš příběh{ICON["arrow"]}</a>
              <a class="btn btn--ghost" href="{FB_DITA}" target="_blank" rel="noopener">Ditin profil na FB{ICON["external"]}</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--tight" id="kontakt" aria-labelledby="kontakt-nadpis">
      <div class="wrap">
        <div class="section-head section-head--center">
          <p class="eyebrow">Kontakt</p>
          <h2 id="kontakt-nadpis" class="reveal">Napište nebo zavolejte.</h2>
          <p class="lead reveal">Nejčerstvější novinky najdete na Facebooku a Instagramu.</p>
        </div>
        <div class="found-steps found-steps--plain">
          <div class="found-step reveal"><h3>Telefon</h3><p><a class="phone" href="tel:{PHONE_TEL}">{PHONE}</a></p></div>
          <div class="found-step reveal" style="--d:.08s"><h3>E-mail</h3><p><a class="phone" href="mailto:{EMAIL}">{EMAIL}</a></p></div>
          <div class="found-step reveal" style="--d:.16s"><h3>Sociální sítě</h3><p><a href="{FB}" target="_blank" rel="noopener">Facebook Depozita</a><br><a href="{IG}" target="_blank" rel="noopener">Instagram @chlupnechlup</a></p></div>
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
        <p class="eyebrow reveal">Kočky k adopci</p>
        <h1 class="reveal" style="--d:.06s">Najděte svou <span class="accent-word">spřízněnou duši</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Tady jsou všichni naši svěřenci, kteří hledají domov. Seznam se načítá z portálu Pesweb.cz, díky kterému můžeme kočky sdílet i na webech obcí a veterinářů.</p>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        {widget("pesweb-adopce", {"shelter": "depozitum-chlup-nechlup"})}
        <p class="center" style="margin-top:20px;color:var(--muted)">Další fotky najdete v <a href="https://www.facebook.com/media/set/?set=a.2506635422737631&amp;type=3" target="_blank" rel="noopener">albu na Facebooku</a>. Nejnovější přírůstky sdílí Dita na <a href="{FB_DITA}" target="_blank" rel="noopener">svém profilu</a>.</p>
      </div>
    </section>

    <section class="section section--sand">
      <div class="wrap">
        <div class="split split--top">
          <div>
            <p class="eyebrow">Podmínky adopce</p>
            <h2 class="reveal">Než si pro kočičku přijedete</h2>
            <p class="reveal">Chcete si pořídit kočičku a pomoct některé z depozita? To je výborná zpráva pro všechny. I pro kočičky, které teprve čekají na ulici, až se v depozitu uvolní teplé místečko.</p>
            <ul class="checklist reveal">
              <li><span>Kočky vydáváme na <strong>adopční smlouvu</strong>, ve které se zavazujete poskytnout kočce stabilní a bezpečný domov.</span></li>
              <li><span>U koťat se zavazujete ke <strong>kastraci v dospělosti</strong>.</span></li>
              <li><span>Prosíme o <strong>závazné rozhodnutí</strong>. Dejte si čas na rozmyšlenou, kočička u nás pár dní i týdnů v pořádku vydrží.</span></li>
            </ul>
          </div>
          <div class="quote-card reveal" style="--d:.1s">
            <h3>Pár všetečných otázek</h3>
            <ul class="checklist" style="margin-bottom:1rem">
              <li><span>Máte nachystaná škrabadla, misky a záchůdky?</span></li>
              <li><span>Spočítali jste si, kolik vyjde kvalitní krmení a veterina?</span></li>
              <li><span>Máte zabezpečený balkon a okna?</span></li>
              <li><span>Víte, kdo se o kočičku postará, když budete na dovolené?</span></li>
            </ul>
            <p style="margin:0;color:var(--muted)">Napište nám, do jakého prostředí kočičku chcete, kdo s vámi sdílí domácnost (pes, další kočka, jak staré děti) a co od ní očekáváte. Uděláme maximum, abychom vám našli perfektní spřízněnou duši.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap wrap--narrow">
        <div class="section-head">
          <p class="eyebrow">Zamítnutá adopce</p>
          <h2 class="reveal">Neúspěch? Nevěšte hlavu.</h2>
          <p class="lead reveal">Může se stát, že vám kočičku nevydáme. Není to proto, že bychom byli zlí nebo si kočky tajně hromadili. Chceme jen, aby nový domov vydržel. Nejčastější důvody:</p>
        </div>
        <div class="faq reveal">
          <details>
            <summary>Pes, který má rád kočky, a kočka, která nemá ráda psy</summary>
            <div class="faq__body"><p>Máte zájem o dospělou kočku zvyklou žít venku a máte pro ni přístup dovnitř i ven, ale na zahradě máte psa. Starší kočky si na psy zvykají špatně a zahradě se pak vyhýbají. V lepším případě se nakonec ubytují u sousedů.</p></div>
          </details>
          <details>
            <summary>Malé děti</summary>
            <div class="faq__body"><p>Chcete dětem pořídit mazlíčka a víte, že odpovědnost nesete vy? Výborně. Pokud jste vybrali kočičku, která se do rušnější domácnosti nehodí, rádi doporučíme jinou.</p><p>Opakovaně se nám ale stává, že malé děti neznají svou sílu a rodiče je neumí nebo nechtějí neustále korigovat. Pak je lepší počkat, až děti povyrostou a pochopí, že s živými tvory se zachází opatrně.</p></div>
          </details>
          <details>
            <summary>Rušná silnice</summary>
            <div class="faq__body"><p>Dospělou kočku zvyklou na ven nebo příliš důvěřivé kotě nevydáme k rušnější silnici. Někdy ani ke klidné cestě, pokud by ji kočka musela často přebíhat, třeba za myšmi na pole. Starší kočky si na nové hrozby zvykají těžko a bývá to pro ně osudné.</p><p>Občas se v depozitu objeví „vítací kotě“, které radostně běží ke všem lidem. Takové raději umístíme do bytu k rodině s dětmi.</p></div>
          </details>
          <details>
            <summary>Další kočky v domácnosti a nemoci</summary>
            <div class="faq__body"><p>Většina koček z depozita pochází z kočičích kolonií, takže bývají k ostatním kočkám nekonfliktní. Důvodem k zamítnutí ale může být zdravotní stav. Když jedna kočka z lokality měla rýmu, chřipku nebo plíseň, často se nemoc postupně projeví i u ostatních z téhož místa.</p><p>Proto kočku z promořené lokality nemůžeme doporučit do domácnosti s dalšími kočkami. Většina kočičích nemocí se přitom na lidi nepřenáší, s výjimkou některých plísní.</p></div>
          </details>
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
        <h1 class="reveal" style="--d:.06s">Příběhy se <span class="accent-word">šťastným koncem</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Naši svěřenci, kteří už svůj domov našli. Všem novým páníčkům děkujeme a přejeme mnoho radostných chvil.</p>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        {widget("pesweb-domov", {"shelter": "depozitum-chlup-nechlup", "statusRelease": ["nasel-domov"], "sort": "updatedAt:desc"})}
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
        <h1 class="reveal" style="--d:.06s">Dočasná péče: domov <span class="accent-word">na přechodnou dobu</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Uvažujete o kočičce, ale nevíte, jestli zvládnete péči na dlouhé roky dopředu? Pak může být dočasná péče, tedy „dočaska“, to pravé pro vás.</p>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        <div class="layout-aside">
          <div class="prose">
            <figure class="reveal"><img src="assets/img/eliot-a-emil.jpg" alt="Koťata Eliot a Emil na škrabadle" loading="lazy" width="960" height="720"><figcaption>Eliot a Emil v domácím depozitu</figcaption></figure>

            <h2>Dočaska není půjčovna koček</h2>
            <p>Depozitovatel se zavazuje starat se o kočičku, dokud nenajde nový domov, nebo alespoň do doby, než se uvolní místo v depozitu. Ve chvíli, kdy kočičku vydáme do dočasky, totiž bereme z ulice další kočky: nemocné, v akutním ohrožení života nebo takové, které už čekají u nálezců.</p>
            <p>Proto není možné vrátit kočku z dočasné péče ze dne na den s tím, že jste si to rozmysleli. Její místo mezitím zabrala kočka z ulice v karanténě a jednotlivá místa jsou navíc rozdělena podle lokality nálezu, aby se při skrytých infekcích nenakazilo celé depozitum. Pro přesouvanou kočku je to obrovský stres.</p>

            <h2>Do dočasek nedáváme nemocné kočky</h2>
            <p>Zvlášť ne začínajícím zájemcům. Naopak potřebujeme dát pryč zdravé kočky, aby se nenakazily. Nemusíte se tedy bát, že budete mít ještě víc práce, starostí a běhání na veterinu.</p>
            <p>Máme i ostřílené dočaskáře, kteří si vezmou těžší případy a v klidu je vypiplají. Patří jim za to naše velké díky.</p>

            <h2>Proč dočasky pomáhají</h2>
            <ul>
              <li>Kočka má celého človíčka na hraní a drbání jen pro sebe, víc se mazlí a zvyká si na lidi.</li>
              <li>V domácím prostředí ji poznáte líp než my v depozitu s dvaceti kočkami. Můžeme tak doplnit její profil a najít jí ty nejlepší zájemce.</li>
              <li>Doma uděláte víc a hezčích fotek, a ty prodávají.</li>
              <li>Uvolníte místo v depozitu pro kočku, která zrovna čeká na ulici.</li>
            </ul>

            <div class="callout">
              <p><strong>Náklady hradí depozitum.</strong> Všechny materiální potřeby koček v dočasné péči platí Depozitum chlup-nechlup. K adopci přednostně nabízíme kočky z dočasek, aby si dočaskáři mohli odpočinout.</p>
            </div>
          </div>
          <aside class="aside-card reveal">
            <h3>Chcete se stát dočaskou?</h3>
            <p>Ozvěte se Ditě. Domluvíte se, jaká kočička by se k vám hodila a co všechno budete potřebovat.</p>
            <div class="btn-row" style="flex-direction:column">
              <a class="btn" href="tel:{PHONE_TEL}">{ICON["phone"]}{PHONE}</a>
              <a class="btn btn--ghost" href="mailto:{EMAIL}?subject=Do%C4%8Dasn%C3%A1%20p%C3%A9%C4%8De">{ICON["mail"]}Napsat e-mail</a>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        {cta_band("Dočasku nezvládnete? I tak můžete pomoct.", "Finanční dar na transparentní účet pokryje kastrace, léky i krmení.", "podporte-nas.html", "Podpořte nás")}
      </div>
    </section>
"""

# ---------------------------------------------------------------------------
# Podpořte nás
# ---------------------------------------------------------------------------

PODPORA = f"""
    <section class="page-hero">
      <div class="wrap">
        <p class="eyebrow reveal">Podpořte nás</p>
        <h1 class="reveal" style="--d:.06s">Bez vás by depozitum <span class="accent-word">nemohlo fungovat</span>.</h1>
        <p class="lead reveal" style="--d:.12s">Nejsme zřizováni městem ani státem. Veškeré náklady na kastrace a ošetření hradíme z darů, případně z vlastní kapsy.</p>
      </div>
    </section>

    <section class="section section--dark section--tight">
      <div class="wrap">
        <div class="donate">
          <div>
            <p class="eyebrow">Transparentní účet</p>
            <h2 class="reveal">Pošlete dar na kočičí účet</h2>
            <p class="lead reveal">Majitelka účtu: Ing. Dita Uhriková · název účtu: Depozitum chlup-nechlup. Pohyby na účtu si můžete kdykoli prohlédnout na stránkách Fio banky.</p>
            <p class="reveal" style="opacity:.8">Ne všechny nákupy pro kočičky jsou z výpisu snadno čitelné, a proto na Facebooku sdílíme i účtenky a faktury v albu <a href="https://www.facebook.com/media/set/?vanity=depozitumchlupnechlup&amp;set=a.3773941716006989" target="_blank" rel="noopener">Transparentní účet</a>.</p>
          </div>
          {account_card("reveal")}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <p class="eyebrow">Další možnosti</p>
          <h2 class="reveal">Pomoct se dá i jinak</h2>
        </div>
        <div class="help-grid" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">
          <a class="help-card reveal" href="kocky-k-adopci.html">
            <div class="help-card__icon">{ICON["home"]}</div>
            <h3>Adopce</h3>
            <p>Nejlepší pomoc je stabilní a bezpečný domov.</p>
            <span class="help-card__more">Kočky k adopci{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.08s" href="docasna-pece.html">
            <div class="help-card__icon">{ICON["paw"]}</div>
            <h3>Dočasná péče</h3>
            <p>Dejte zdravé kočce domov, než najde ten trvalý.</p>
            <span class="help-card__more">Jak to funguje{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.16s" href="{FB}" target="_blank" rel="noopener">
            <div class="help-card__icon">{ICON["share"]}</div>
            <h3>Sdílení</h3>
            <p>Sdílejte naše kočičky na Facebooku nebo na inzertních portálech jako Annonce a Bazoš.</p>
            <span class="help-card__more">Facebook Depozita{ICON["arrow"]}</span>
          </a>
          <a class="help-card reveal" style="--d:.24s" href="mailto:{EMAIL}?subject=Inzerce%20ko%C4%8Dek">
            <div class="help-card__icon">{ICON["search"]}</div>
            <h3>Inzerce</h3>
            <p>Máte web obce, veterinární ordinace nebo firmy? Kočky k adopci na něj můžete vložit přes Pesweb.cz.</p>
            <span class="help-card__more">Napište nám{ICON["arrow"]}</span>
          </a>
        </div>
      </div>
    </section>

    <section class="section section--sand section--tight">
      <div class="wrap wrap--narrow center">
        <p class="statement" data-words style="margin-inline:auto">Za deset let by nebylo možné zachránit tolik kočiček a tolik životů, <em>nebýt vašich darů</em>. Děkujeme.</p>
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
        <p class="lead reveal" style="--d:.12s">Obec má ze zákona povinnost postarat se o toulavé zvíře, o kočku stejně jako o psa. Tady je postup, který opravdu pomáhá. S laskavým svolením autorky Evy Hulcové.</p>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        <div class="found-steps">
          <div class="found-step reveal"><h3>Městská policie</h3><p>Kde ji mají, volejte <a class="phone" href="tel:156">156</a></p></div>
          <div class="found-step reveal" style="--d:.08s"><h3>Starosta obce</h3><p>Kde městská policie není, volejte starostovi nebo na odbor životního prostředí.</p></div>
          <div class="found-step reveal" style="--d:.16s"><h3>Až potom útulek</h3><p>Když na obci narazíte, ozvěte se nám. Poradíme a pomůžeme.</p></div>
        </div>
      </div>
    </section>

    <section class="section section--tight">
      <div class="wrap">
        <div class="layout-aside">
          <div class="prose">
            <ol>
              <li><strong>Nepište nejdřív na Facebook a nevolejte hned do útulků.</strong></li>
              <li><strong>Občanský zákoník, § 1058 odst. 1:</strong> Je-li nalezeno zvíře, u něhož je zjevné, že mělo vlastníka, oznámí nálezce nález bez zbytečného odkladu obci, nelze-li z okolností poznat, komu má být vráceno. Obec má povinnost postarat se o toulavé zvíře, o psa stejně jako o kočku.</li>
              <li>Tam, kde je městská policie, volejte <a href="tel:156">156</a>. Kde není, volejte odbor životního prostředí, ale především si najděte číslo na starostu obce.</li>
              <li>Volat musíte starostovi nebo městské policii <strong>v místě, kde jste kočičku našli</strong>, ne do jiného města.</li>
              <li>Volejte na obec tak, jako voláte nám: ve dne, pozdě večer, o svátku i v neděli. Městská policie i starosta za svou práci dostávají plat, my pomáháme zadarmo. Nestyďte se, takhle je to správně.</li>
              <li>Do útulku volejte, až když na obci narazíte. Mnoho obcí zákony nezná. Nahrávejte hovor, stěžujte si, chtějte odmítnutí písemně. Správný útulek vám poradí, pomůže a zavolá starostovi.</li>
              <li>Každá nenahlášená kočka je pro obec „neviditelná“. Obce pak tvrdí, že problém s kočkami nemají, a celý systém se nemůže zlepšit.</li>
              <li>Pokud obec kočku přijme, sledujte její další osud. Kočka musí být obcí zaevidovaná a vyhlášená na úřední desce, aby se mohl dohledat případný majitel. Předem upozorněte, že se budete zajímat.</li>
              <li>Nedávejte kočky do pochybných útulků, které zvířata hromadí a nevydávají. Správný útulek poznáte podle toho, že má IČO, sbírkový účet, výroční zprávy, web s datem a místem nálezu koček, nemá extrémní úmrtnost a nalezené kočky hlásí obcím.</li>
            </ol>
            <blockquote>
              <p>Prosím nálezce, aby na nás brali ohled. Je nás málo a chodíme do vlastní práce. Postupujte prosím podle návodu a podle zákona právě proto, aby se podmínky pro toulavé kočky v naší zemi změnily. Moc děkuji. Sdílejte prosím.</p>
              <p style="margin:0"><strong>Eva Hulcová</strong></p>
            </blockquote>
            <div class="callout">
              <p><strong>Ztratil se vám mazlíček?</strong> Zkuste službu <a href="https://najdimazlicka.cz/" target="_blank" rel="noopener">Najdi mazlíčka</a>, která hledá ztracená zvířata po celé republice pomocí kampaní na sociálních sítích.</p>
            </div>
          </div>
          <aside class="aside-card reveal">
            <h3>Obec odmítla?</h3>
            <p>Ozvěte se nám. Rádi poradíme, jak postupovat, a pomůžeme s jednáním s obcí.</p>
            <div class="btn-row" style="flex-direction:column">
              <a class="btn" href="tel:{PHONE_TEL}">{ICON["phone"]}{PHONE}</a>
              <a class="btn btn--ghost" href="mailto:{EMAIL}?subject=Nalezen%C3%A1%20ko%C4%8Dka">{ICON["mail"]}Napsat e-mail</a>
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
        <p class="lead reveal" style="--d:.12s">Depozitum chlup-nechlup je domácí soukromé zařízení na odchyt a léčbu koček ze Strakonic a okolí.</p>
      </div>
    </section>

    <section class="section section--tight" style="padding-top:0">
      <div class="wrap">
        <div class="split">
          <div class="split__media reveal" data-progress><img src="assets/img/mourek.jpg" alt="Mourovatá kočka odpočívá na huňaté dece" loading="lazy"></div>
          <div class="prose">
            <h2 class="mt-0">Jak to celé začalo</h2>
            <p>Depozitum vzniklo před více než deseti lety jako malé rodinné zázemí pro nalezené kočičky z okolí. Postupně se rozrostlo do dnešní velikosti.</p>
            <p>Kapacita depozita je <strong>20 míst</strong>. Kvůli karanténám, stálým a starším kočičkám, které je těžké umístit, a hlavně kvůli nemocem musíme kočky z různých lokalit ubytovávat odděleně a důsledně dodržovat hygienická opatření.</p>
            <p>Za rok se v depozitu vystřídá zhruba <strong>100 až 120 koček</strong>. To je kapacita kočičího útulku v Českých Budějovicích, kde se přitom odchytem zvířat zabývá hned několik organizací.</p>
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
            <p>Zakladatelkou, organizátorkou, páteří, ale především srdcem celého depozita je Dita Uhriková. Patří jí nesmírný dík a obdiv za vytrvalý boj s kočičími nemocemi a zraněními. Ani po letech vyčerpávajícího úsilí stále není hotovo: na ulicích se pořád objevují nové kočičky i s koťaty.</p>
            <p>Rozhovor s Ditou si můžete přečíst na portálu <a href="https://www.jcted.cz/dita-uhrikova-bojuje-za-kocici-utulek-za-obce-hasime-problemy-z-urazek-na-internetu-si-nic-nedelam-rika/" target="_blank" rel="noopener">Jižní Čechy Teď</a>.</p>

            <h2>Strakonice stále nemají kočičí útulek</h2>
            <p>Zvlášť v době jarních koťat se snažíme depozitum „nafouknout“ a obsadit každou dočasnou péči, která je jen trochu možná. Kapacitou ale nemůžeme pokrýt péči o všechny nechtěné a toulavé kočky ze Strakonic a přilehlých obcí.</p>
            <p>Město Strakonice přesto i nadále odmítá zřídit útulek pro kočky. Povinnosti, které obci ukládá zákon, přitom není možné přenášet na její občany.</p>

            <h2>Kdo nám pomáhá</h2>
            <p>Velkou pomocí jsou organizace jako <a href="https://www.feliti.cz/" target="_blank" rel="noopener">Feliti</a>, které proplácejí kastrace koček i „běžným smrtelníkům“. Podporujeme také spolek Obce kastrují, který šíří osvětu o nutnosti kastrace koček.</p>
            <div class="callout"><p><strong>Kastrovat, kastrovat, kastrovat.</strong> Místo toho, aby koček za léta našeho působení ubývalo, zdá se, že je to naopak. Jediná cesta ven je důsledná kastrace, i u koček „na dvoře“.</p></div>
          </div>
          <aside class="aside-card reveal">
            <h3>Sledujte nás</h3>
            <p>Nejnovější informace najdete na Facebooku Depozita, absolutně žhavé novinky pak na Ditině osobním profilu.</p>
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
        {cta_band("Chcete nám pomoct?", "Adopcí, dočasnou péčí, darem nebo jen sdílením. Každá pomoc uvolní místo další kočce.", "podporte-nas.html", "Jak pomoct")}
      </div>
    </section>
"""

FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="14" fill="#d4612a"/><g fill="#fffaf2" transform="translate(6 6) scale(.75)">' + ICON["paw"][ICON["paw"].index(">") + 1:-6] + "</g></svg>"

if __name__ == "__main__":
    (OUT / "assets/img/favicon.svg").write_text(FAVICON, encoding="utf-8")
    page("index.html", "Depozitum chlup-nechlup · Kočky z ulice hledají domov", "Domácí depozitum pro odchyt, léčbu a kastraci koček ze Strakonic a okolí. Kočky k adopci, dočasná péče a transparentní účet.", INDEX)
    page("kocky-k-adopci.html", "Kočky k adopci", "Kočky z Depozita chlup-nechlup, které hledají stabilní a bezpečný domov. Podmínky adopce a nejčastější dotazy.", ADOPCE)
    page("nasli-domov.html", "Domov našli", "Kočky z Depozita chlup-nechlup, které už našly nový domov.", NASLI)
    page("docasna-pece.html", "Dočasná péče", "Jak funguje domácí depozitum neboli dočasná péče o kočky z Depozita chlup-nechlup.", DOCASKA)
    page("podporte-nas.html", "Podpořte nás", "Transparentní účet 6077760777/2010 a další způsoby, jak podpořit Depozitum chlup-nechlup.", PODPORA)
    page("nasli-jste-kocku.html", "Našli jste kočku?", "Co dělat, když najdete toulavou kočku: komu volat a jak postupovat podle zákona.", NALEZ)
    page("o-nas.html", "O nás", "Příběh Depozita chlup-nechlup a jeho zakladatelky Dity Uhrikové.", ONAS)
