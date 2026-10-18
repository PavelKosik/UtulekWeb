/* Depozitum chlup-nechlup — interakce a scroll animace (bez knihoven) */
(function () {
  "use strict";

  var root = document.documentElement;
  window.__siteReady = true; // pojistka v <head> už nemusí zobrazovat obsah bez animací
  root.classList.remove("js-off");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Menu na mobilu ---------- */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.querySelectorAll(".nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        document.body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("nav-open")) {
        document.body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* ---------- Rozdělení prohlášení na slova ---------- */
  var statements = [].slice.call(document.querySelectorAll("[data-words]"));
  statements.forEach(function (el) {
    var walk = function (node) {
      [].slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var span = document.createElement("span");
            span.className = "w";
            span.textContent = part;
            frag.appendChild(span);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          walk(child);
        }
      });
    };
    walk(el);
    el._words = [].slice.call(el.querySelectorAll(".w"));
  });

  /* ---------- Objevování prvků ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- Počítadla ---------- */
  var counters = document.querySelectorAll("[data-count]");
  var runCounter = function (el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var suffix = el.getAttribute("data-suffix") || "";
    var fmt = function (n) { return n.toLocaleString("cs-CZ"); };
    if (reduceMotion) { el.textContent = fmt(target) + suffix; return; }
    var start = null;
    var dur = 1600;
    var step = function (t) {
      if (!start) start = t;
      var k = Math.min(1, (t - start) / dur);
      var eased = 1 - Math.pow(1 - k, 4);
      el.textContent = fmt(Math.round(target * eased)) + suffix;
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  if ("IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { runCounter(entry.target); cio.unobserve(entry.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  } else {
    counters.forEach(runCounter);
  }

  /* ---------- Cesta kočky: aktivní krok podle scrollu ---------- */
  var journey = document.querySelector("[data-journey]");
  var steps = journey ? [].slice.call(journey.querySelectorAll(".journey__step")) : [];
  var slides = journey ? [].slice.call(journey.querySelectorAll(".journey__media img")) : [];
  var bars = journey ? [].slice.call(journey.querySelectorAll(".journey__meter span")) : [];
  var label = journey ? journey.querySelector(".journey__label") : null;
  var activeStep = -1;

  /* ---------- Hlavní scroll smyčka ---------- */
  var header = document.querySelector(".site-header");
  var heroes = document.querySelectorAll(".hero, .page-hero");
  var parallax = [].slice.call(document.querySelectorAll("[data-progress]"));
  var marquees = [].slice.call(document.querySelectorAll("[data-marquee]"));
  var lastY = window.scrollY;
  var ticking = false;

  var clamp = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };

  var update = function () {
    ticking = false;
    // 1) Nejdřív všechna měření, pak všechny zápisy: prohlížeč pak nemusí
    //    přepočítávat layout po každém kroku (forced reflow).
    var y = window.scrollY;
    var vh = window.innerHeight;
    var docH = root.scrollHeight - vh;
    var navOpen = document.body.classList.contains("nav-open");
    var heroH = [], para = [], mq = [], stmt = [], stepRects = [];
    if (!reduceMotion) {
      heroes.forEach(function (h) { heroH.push(h.offsetHeight); });
      parallax.forEach(function (el) { para.push(el.getBoundingClientRect()); });
      marquees.forEach(function (el) { mq.push([el.getBoundingClientRect(), el.firstElementChild.scrollWidth, el.clientWidth]); });
      statements.forEach(function (el) { stmt.push(el.getBoundingClientRect()); });
      steps.forEach(function (s) { stepRects.push(s.getBoundingClientRect()); });
    }

    // 2) Zápisy
    root.style.setProperty("--page-progress", docH > 0 ? clamp(y / docH).toFixed(4) : 0);
    if (header) {
      header.classList.toggle("is-scrolled", y > 12);
      header.classList.toggle("is-hidden", y > lastY && y > 420 && !navOpen);
    }
    lastY = y;

    if (reduceMotion) return;

    heroes.forEach(function (h, i) {
      h.style.setProperty("--hero-p", clamp(y / Math.max(1, heroH[i])).toFixed(4));
    });

    // --p: 0 když prvek vjíždí zespodu, 1 když opouští horní okraj
    parallax.forEach(function (el, i) {
      var r = para[i];
      if (r.bottom < -100 || r.top > vh + 100) return;
      el.style.setProperty("--p", clamp((vh - r.top) / (vh + r.height)).toFixed(4));
    });

    marquees.forEach(function (el, i) {
      var r = mq[i][0];
      if (r.bottom < 0 || r.top > vh) return;
      var p = clamp((vh - r.top) / (vh + r.height));
      el.firstElementChild.style.setProperty("--mq", (p * Math.max(0, mq[i][1] - mq[i][2])).toFixed(1));
    });

    statements.forEach(function (el, i) {
      var r = stmt[i];
      // rozsvěcování začne, když je text v 90 % výšky okna; celý svítí, když jeho střed dojede doprostřed
      var lit = Math.round(clamp((vh * 0.9 - r.top) / (vh * 0.4 + r.height * 0.5)) * el._words.length);
      if (lit === el._lit) return;
      el._lit = lit;
      el._words.forEach(function (w, j) { w.classList.toggle("is-lit", j < lit); });
    });

    if (steps.length) {
      var mid = vh * 0.5;
      var current = 0;
      stepRects.forEach(function (r, i) {
        if (r.top < mid) current = i;
        if (bars[i]) bars[i].style.setProperty("--fill", clamp((mid - r.top) / Math.max(1, r.height)).toFixed(3));
      });
      if (current !== activeStep) {
        activeStep = current;
        steps.forEach(function (s, i) { s.classList.toggle("is-active", i === current); });
        slides.forEach(function (img, i) { img.classList.toggle("is-active", i === current); });
        if (label) label.textContent = steps[current].getAttribute("data-label") || "";
      }
    }
  };

  var onScroll = function () {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  update();

  if (reduceMotion) {
    statements.forEach(function (el) { el._words.forEach(function (w) { w.classList.add("is-lit"); }); });
    steps.forEach(function (s) { s.classList.add("is-active"); });
    if (slides[0]) slides[0].classList.add("is-active");
  }

  /* ---------- Widget Pesweb: načte se, až když je na dohled ---------- */
  var peswebScript = null;
  var loadPesweb = function (cb) {
    if (window.PeswebWidget) { cb(); return; }
    if (!peswebScript) {
      peswebScript = document.createElement("script");
      peswebScript.src = "https://www.pesweb.cz/widget/pesweb-widget.min.js";
      peswebScript.async = true;
      document.head.appendChild(peswebScript);
    }
    peswebScript.addEventListener("load", cb);
  };
  var initWidget = function (el) {
    if (el._ready) return;
    el._ready = true;
    loadPesweb(function () {
      try {
        var cfg = JSON.parse(el.getAttribute("data-pesweb"));
        cfg.container = el;
        window.PeswebWidget.init(cfg);
        // widget dává iframu role="region", což iframe mít nesmí (WCAG); název má z title
        var frame = el.querySelector("iframe");
        if (frame) frame.removeAttribute("role");
      } catch (e) { /* zůstane záložní odkaz */ }
    });
  };
  var widgets = [].slice.call(document.querySelectorAll("[data-pesweb]"));
  if ("IntersectionObserver" in window) {
    var wio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && !entry.target.closest("[hidden]")) { initWidget(entry.target); wio.unobserve(entry.target); }
      });
    }, { rootMargin: "600px 0px" });
    widgets.forEach(function (el) { wio.observe(el); });
  } else {
    widgets.forEach(initWidget);
  }

  /* ---------- Filtry koček (věk, pohlaví, řazení) — přenačtou widget, stav je v adrese ---------- */
  var filterForm = document.querySelector("[data-cat-filters]");
  var filterWidget = filterForm && document.querySelector("[data-pesweb]");
  if (filterForm && filterWidget) {
    var note = document.querySelector("[data-filter-note]");
    var params = new URLSearchParams(location.search);
    ["vek", "pohlavi", "razeni"].forEach(function (name) {
      var wanted = params.get(name);
      if (!wanted) return;
      var input = filterForm.querySelector('input[name="' + name + '"][value="' + wanted + '"]');
      if (input) input.checked = true;
    });
    var applyFilters = function (push) {
      var cfg = JSON.parse(filterWidget.getAttribute("data-pesweb"));
      var get = function (name) { return filterForm.querySelector('input[name="' + name + '"]:checked'); };
      var vek = get("vek"), pohlavi = get("pohlavi"), razeni = get("razeni");
      cfg.filters = { shelter: cfg.filters.shelter, sort: razeni.getAttribute("data-api") };
      if (vek.value) cfg.filters.age = vek.getAttribute("data-api");
      if (pohlavi.value) cfg.filters.sex = pohlavi.getAttribute("data-api");
      filterWidget.setAttribute("data-pesweb", JSON.stringify(cfg));
      if (note) note.hidden = !(razeni.value === "nejdele" || vek.value === "seniori" || vek.value === "dospele");
      if (push) {
        var q = new URLSearchParams();
        if (vek.value) q.set("vek", vek.value);
        if (pohlavi.value) q.set("pohlavi", pohlavi.value);
        if (razeni.value) q.set("razeni", razeni.value);
        history.replaceState(null, "", location.pathname + (q.toString() ? "?" + q : "") + location.hash);
      }
      filterWidget._ready = false;
      initWidget(filterWidget);
    };
    if (location.search) applyFilters(false);
    filterForm.addEventListener("change", function () { applyFilters(true); });

    // Když filtru nic neodpovídá, widget hlásí malou výšku a píše „nemáme žádné kočky“; doplníme vysvětlení.
    var empty = document.querySelector("[data-filter-empty]");
    window.addEventListener("message", function (e) {
      if (!empty || e.origin !== "https://www.pesweb.cz" || !e.data || e.data.type !== "pesweb-widget-height") return;
      var frame = filterWidget.querySelector("iframe");
      if (!frame || e.source !== frame.contentWindow) return;
      var filtered = filterForm.querySelector('input[name="vek"]:checked').value || filterForm.querySelector('input[name="pohlavi"]:checked').value;
      empty.hidden = !(filtered && e.data.height <= 410); // prázdný widget má výšku 400 px
    });
  }

  /* ---------- Záložky ---------- */
  document.querySelectorAll("[role='tablist']").forEach(function (list) {
    var tabs = [].slice.call(list.querySelectorAll("[role='tab']"));
    var select = function (tab) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
        if (on && panel) panel.querySelectorAll("[data-pesweb]").forEach(initWidget);
      });
    };
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!d) return;
        var next = tabs[(i + d + tabs.length) % tabs.length];
        select(next);
        next.focus();
      });
    });
  });

  /* ---------- Volba částky daru: přepne QR kód a popis ---------- */
  document.querySelectorAll("[data-amounts]").forEach(function (box) {
    var buttons = [].slice.call(box.querySelectorAll("[data-amount]"));
    var card = box.closest(".account");
    var qr = card && card.querySelector(".account__qr img");
    var caption = card && card.querySelector(".account__qr span");
    var impact = card && card.querySelector(".impact");
    var save = card && card.querySelector(".qr-save");
    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        buttons.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        var amount = b.getAttribute("data-amount");
        if (qr) {
          qr.src = b.getAttribute("data-qr");
          qr.alt = amount ? "QR platba " + amount + " Kč na transparentní účet" : "QR platba na transparentní účet";
        }
        if (caption) caption.textContent = amount ? "QR platba " + amount + " Kč" : "QR platba, částku zadáte v aplikaci banky";
        if (impact) impact.innerHTML = b.getAttribute("data-impact");
        if (save) {
          save.href = b.getAttribute("data-png");
          save.setAttribute("download", "qr-platba-depozitum" + (amount ? "-" + amount : "") + ".png");
        }
      });
    });
  });

  /* ---------- Sdílení ---------- */
  document.querySelectorAll("[data-share]").forEach(function (box) {
    var url = box.getAttribute("data-url") ? new URL(box.getAttribute("data-url"), location.href).href : location.href.split("#")[0];
    var text = box.getAttribute("data-share") || document.title;
    var fb = box.querySelector("[data-share-fb]");
    var wa = box.querySelector("[data-share-wa]");
    var native = box.querySelector("[data-share-native]");
    var copy = box.querySelector("[data-share-copy]");
    if (fb) fb.href = "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(url);
    if (wa) wa.href = "https://wa.me/?text=" + encodeURIComponent(text + " " + url);
    if (native) {
      if (navigator.share) {
        native.addEventListener("click", function () { navigator.share({ title: document.title, text: text, url: url }).catch(function () {}); });
      } else {
        native.hidden = true;
      }
    }
    if (copy) copy.setAttribute("data-copy", url);
  });

  /* ---------- Kopírování (číslo účtu, odkazy) ---------- */
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    if (btn._copyBound) return;
    btn._copyBound = true;
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      var label = btn.querySelector("span") || btn;
      var original = label.textContent;
      var done = function () {
        btn.classList.add("copy-done");
        label.textContent = "Zkopírováno";
        setTimeout(function () { btn.classList.remove("copy-done"); label.textContent = original; }, 2200);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { window.prompt("Zkopírujte:", text); });
      } else {
        window.prompt("Zkopírujte:", text);
      }
    });
  });

  /* ---------- Dotazníky: z odpovědí sestaví zprávu pro Ditu (web nic neukládá ani neodesílá) ---------- */
  document.querySelectorAll("[data-qform]").forEach(function (form) {
    var kind = form.getAttribute("data-qform");
    var preview = form.querySelector("[data-qform-preview]");
    var previewWrap = form.querySelector("[data-qform-preview-wrap]");
    var error = form.querySelector("[data-qform-error]");
    var field = function (name) { return form.querySelector('[name="' + name + '"]'); };
    var val = function (name) {
      var el = form.querySelector('[name="' + name + '"]:checked') || form.querySelector('input:not([type=radio]):not([type=checkbox])[name="' + name + '"], textarea[name="' + name + '"]');
      return el ? el.value.trim() : "";
    };
    var vals = function (name) { return [].slice.call(form.querySelectorAll('[name="' + name + '"]:checked')).map(function (el) { return el.value; }); };
    var sentence = function (t) { return t.charAt(0).toUpperCase() + t.slice(1); };

    var wanted = new URLSearchParams(location.search).get("kocka");
    if (wanted && field("kocka")) field("kocka").value = wanted;

    var compose = function () {
      var L = ["Dobrý den,"];
      var obec = val("obec"), bydleni = val("bydleni");
      if (kind === "adopce") {
        var kocka = val("kocka");
        L.push(kocka ? "mám zájem o adopci: " + kocka + "." : "mám zájem o adopci kočičky a nechám si poradit, která by se k nám hodila.");
        L.push("");
        if (bydleni || obec) L.push("Bydlím " + (bydleni || "") + (obec ? (bydleni ? " (obec " + obec + ")" : "v obci " + obec) : "") + ".");
        if (val("ven")) L.push("Kočka " + val("ven") + ".");
        if (val("site")) L.push("Sítě na oknech a balkoně: " + val("site") + ".");
        var dom = vals("domacnost");
        if (dom.length) {
          L.push("Bydlí s námi: " + dom.map(function (d) { return d === "děti" && val("vek_deti") ? "děti (" + val("vek_deti") + ")" : d; }).join(", ") + ".");
        }
        if (val("zkusenosti")) L.push(sentence(val("zkusenosti")) + ".");
        if (val("sama")) L.push(val("sama") === "skoro vůbec" ? "Přes den kočka skoro nebude sama." : "Přes den bude kočka sama " + val("sama") + ".");
        if (val("dovolena")) L.push("Když budeme pryč, postará se: " + val("dovolena") + ".");
        if (val("ocekavani")) L.push("Co od kočičky čekáme: " + val("ocekavani"));
        if (field("podminky") && field("podminky").checked) { L.push(""); L.push("Podmínky adopce (adopční smlouva, kastrace koťat v dospělosti) beru na vědomí."); }
      } else {
        L.push("zajímá mě dočasná péče o kočičku.");
        L.push("");
        if (bydleni || obec) L.push("Bydlím " + (bydleni || "") + (obec ? (bydleni ? " (obec " + obec + ")" : "v obci " + obec) : "") + ".");
        if (val("mistnost")) L.push(val("mistnost") === "ano" ? "Samostatnou místnost pro kočku mám." : "Samostatnou místnost pro kočku nemám.");
        var zv = vals("zvirata");
        if (zv.length) L.push(zv.indexOf("nemám") !== -1 ? "Doma žádná zvířata nemám." : "Doma mám: " + zv.join(", ") + ".");
        var delka = val("delka");
        if (delka) L.push(delka === "dokud nenajde domov" ? "Kočku si můžu nechat, dokud nenajde domov." : "Kočku si můžu vzít " + delka + ".");
        var koho = val("koho");
        if (koho) L.push(koho === "je mi to jedno" ? "Je mi jedno, jestli koťata, nebo dospělou kočku." : "Nejraději " + koho + ".");
      }
      L.push("");
      if (val("jmeno")) L.push(val("jmeno"));
      if (val("telefon")) L.push("Tel.: " + val("telefon"));
      return L.join("\n");
    };

    var refresh = function () {
      form.querySelectorAll("[data-show-if]").forEach(function (el) {
        var parts = el.getAttribute("data-show-if").split("=");
        el.hidden = vals(parts[0]).indexOf(parts[1]) === -1;
      });
      // „nemám“ zvířata vylučuje ostatní volby
      var none = form.querySelector('[name="zvirata"][value="nemám"]');
      if (none && none.checked) form.querySelectorAll('[name="zvirata"]:not([value="nemám"])').forEach(function (el) { el.checked = false; });
      var answered = [].slice.call(form.elements).some(function (el) { return (el.type === "radio" || el.type === "checkbox") ? el.checked : el.value && el.value.trim(); });
      if (previewWrap) previewWrap.hidden = !answered;
      if (preview) preview.textContent = compose();
    };
    form.addEventListener("input", refresh);
    form.addEventListener("change", function (e) {
      if (e.target.name === "zvirata" && e.target.value !== "nemám" && e.target.checked) {
        var none = form.querySelector('[name="zvirata"][value="nemám"]');
        if (none) none.checked = false;
      }
      refresh();
    });
    refresh();

    var validate = function () {
      var missing = [];
      ["jmeno", "telefon"].forEach(function (n) { var el = field(n); if (el && !el.value.trim()) missing.push(el); });
      var cond = field("podminky");
      if (cond && !cond.checked) missing.push(cond);
      form.querySelectorAll("[aria-invalid]").forEach(function (el) { el.removeAttribute("aria-invalid"); });
      if (!missing.length) { if (error) error.hidden = true; return true; }
      missing.forEach(function (el) { el.setAttribute("aria-invalid", "true"); });
      if (error) {
        var needContact = missing.some(function (el) { return el.name !== "podminky"; });
        error.textContent = (needContact ? "Doplňte prosím jméno a telefon, ať se vám Dita může ozvat. " : "") + (cond && !cond.checked ? "Potvrďte prosím podmínky adopce." : "");
        error.hidden = false;
      }
      missing[0].focus();
      return false;
    };

    // Odeslání (tlačítko i Enter): e-mail připravený z odpovědí. Bez JavaScriptu formulář použije action="mailto:".
    var mailBtn = form.querySelector("[data-qform-mail]");
    if (mailBtn) form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) return;
      var subject = mailBtn.getAttribute("data-subject") + (val("kocka") ? " – " + val("kocka") : "");
      location.href = "mailto:" + form.getAttribute("data-to") + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(compose().replace(/\n/g, "\r\n"));
    });
    var smsBtn = form.querySelector("[data-qform-sms]");
    if (smsBtn) smsBtn.addEventListener("click", function () {
      if (!validate()) return;
      location.href = "sms:" + form.getAttribute("data-sms") + "?&body=" + encodeURIComponent(compose());
    });
    var copyBtn = form.querySelector("[data-qform-copy]");
    if (copyBtn) copyBtn.addEventListener("click", function () {
      if (!validate()) return;
      var text = compose();
      var label = copyBtn.querySelector("span");
      var done = function () { copyBtn.classList.add("copy-done"); label.textContent = "Zkopírováno"; setTimeout(function () { copyBtn.classList.remove("copy-done"); label.textContent = "Zkopírovat zprávu"; }, 2200); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { window.prompt("Zkopírujte zprávu:", text); });
      else window.prompt("Zkopírujte zprávu:", text);
    });
  });

  /* ---------- Spodní lišta na mobilu: ukáže se mimo úvod, patičku a sekci daru ---------- */
  var cta = document.querySelector(".mobile-cta");
  if (cta && "IntersectionObserver" in window) {
    var blockers = [].slice.call(document.querySelectorAll(".hero, .page-hero, .site-footer, #dar"));
    var bio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { e.target._inView = e.isIntersecting; });
      cta.classList.toggle("is-visible", !blockers.some(function (b) { return b._inView; }));
    });
    blockers.forEach(function (b) { bio.observe(b); });
  }

  /* ---------- Rok v patičce ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
