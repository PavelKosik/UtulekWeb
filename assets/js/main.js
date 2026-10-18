/* Depozitum chlup-nechlup — interakce a scroll animace (bez knihoven) */
(function () {
  "use strict";

  var root = document.documentElement;
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

  /* ---------- Kopírování čísla účtu ---------- */
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      var label = btn.querySelector("span");
      var original = label ? label.textContent : "";
      var done = function () {
        btn.classList.add("copy-done");
        if (label) label.textContent = "Zkopírováno";
        setTimeout(function () {
          btn.classList.remove("copy-done");
          if (label) label.textContent = original;
        }, 2200);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { window.prompt("Číslo účtu:", text); });
      } else {
        window.prompt("Číslo účtu:", text);
      }
    });
  });

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
    if (reduceMotion) { el.textContent = target + suffix; return; }
    var start = null;
    var dur = 1600;
    var step = function (t) {
      if (!start) start = t;
      var k = Math.min(1, (t - start) / dur);
      var eased = 1 - Math.pow(1 - k, 4);
      el.textContent = Math.round(target * eased) + suffix;
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
    var y = window.scrollY;
    var vh = window.innerHeight;
    var docH = document.documentElement.scrollHeight - vh;

    root.style.setProperty("--page-progress", docH > 0 ? clamp(y / docH).toFixed(4) : 0);

    if (header) {
      header.classList.toggle("is-scrolled", y > 12);
      var goingDown = y > lastY;
      header.classList.toggle("is-hidden", goingDown && y > 420 && !document.body.classList.contains("nav-open"));
    }
    lastY = y;

    if (reduceMotion) return;

    heroes.forEach(function (h) {
      var p = clamp(y / Math.max(1, h.offsetHeight));
      h.style.setProperty("--hero-p", p.toFixed(4));
    });

    // --p: 0 když prvek vjíždí zespodu, 1 když opouští horní okraj
    parallax.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) return;
      el.style.setProperty("--p", clamp((vh - r.top) / (vh + r.height)).toFixed(4));
    });

    marquees.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      var track = el.firstElementChild;
      var max = Math.max(0, track.scrollWidth - el.clientWidth);
      var p = clamp((vh - r.top) / (vh + r.height));
      track.style.setProperty("--mq", (p * max).toFixed(1));
    });

    statements.forEach(function (el) {
      var r = el.getBoundingClientRect();
      // osvětlení začne, když je text v 85 % výšky okna, a skončí ve 35 %
      var p = clamp((vh * 0.85 - r.top) / (vh * 0.5 + r.height * 0.6));
      var lit = Math.round(p * el._words.length);
      el._words.forEach(function (w, i) { w.classList.toggle("is-lit", i < lit); });
    });

    if (steps.length) {
      var mid = vh * 0.5;
      var current = 0;
      steps.forEach(function (s, i) {
        var r = s.getBoundingClientRect();
        if (r.top < mid) current = i;
        var fill = clamp((mid - r.top) / Math.max(1, r.height));
        if (bars[i]) bars[i].style.setProperty("--fill", fill.toFixed(3));
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

  /* ---------- Rok v patičce ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
