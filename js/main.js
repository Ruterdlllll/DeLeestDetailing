/* ============================================================
   De Leest Detailing — interactions
   ============================================================ */

(function () {
  "use strict";

  /* ---------- Language toggle ---------- */
  const STORAGE_KEY = "dld-lang";
  const langButtons = document.querySelectorAll(".lang-btn");

  function applyLang(lang) {
    const dict = I18N[lang] || I18N.en;

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (dict[key]) el.textContent = dict[key];
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (dict[key]) el.setAttribute("placeholder", dict[key]);
    });

    document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
      const key = el.getAttribute("data-i18n-aria");
      if (dict[key]) el.setAttribute("aria-label", dict[key]);
    });

    document.querySelectorAll("[data-i18n-content]").forEach((el) => {
      const key = el.getAttribute("data-i18n-content");
      if (dict[key]) el.setAttribute("content", dict[key]);
    });

    document.documentElement.setAttribute("lang", lang);
    langButtons.forEach((btn) =>
      btn.classList.toggle("active", btn.dataset.lang === lang)
    );

    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* private mode */ }
  }

  function currentLang() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && I18N[saved]) return saved;
    } catch (e) { /* private mode */ }
    return "nl";
  }

  langButtons.forEach((btn) =>
    btn.addEventListener("click", () => applyLang(btn.dataset.lang))
  );
  applyLang(currentLang());

  /* ---------- Sticky header + floating page nav ---------- */
  const header = document.getElementById("siteHeader");
  const pageNavTop = document.getElementById("pageNavTop");
  const pageNavBottom = document.getElementById("pageNavBottom");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function scrollToY(y) {
    window.scrollTo({ top: y, behavior: reduceMotion ? "auto" : "smooth" });
  }

  if (header && pageNavTop && pageNavBottom) {
    pageNavTop.addEventListener("click", () => scrollToY(0));
    pageNavBottom.addEventListener("click", () =>
      scrollToY(document.documentElement.scrollHeight)
    );

    function onScroll() {
      const y = window.scrollY;
      header.classList.toggle("scrolled", y > 24);
      pageNavTop.classList.toggle("hidden", y < 300);
      pageNavBottom.classList.toggle(
        "hidden",
        y + window.innerHeight >= document.documentElement.scrollHeight - 120
      );
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Mobile menu ---------- */
  const navToggle = document.getElementById("navToggle");
  const mainNav = document.getElementById("mainNav");

  if (navToggle && mainNav) {
    navToggle.addEventListener("click", () => {
      const open = mainNav.classList.toggle("open");
      navToggle.classList.toggle("open", open);
      navToggle.setAttribute("aria-expanded", String(open));
    });

    mainNav.querySelectorAll("a").forEach((link) =>
      link.addEventListener("click", () => {
        mainNav.classList.remove("open");
        navToggle.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
      })
    );

    /* Tap anywhere outside the open menu closes it */
    document.addEventListener("click", (event) => {
      if (!mainNav.classList.contains("open")) return;
      if (mainNav.contains(event.target) || navToggle.contains(event.target)) return;
      mainNav.classList.remove("open");
      navToggle.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    revealEls.forEach((el) => observer.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("visible"));
  }

  /* ---------- Contact form (Formspree) ---------- */
  const form = document.getElementById("contactForm");
  const status = document.getElementById("formStatus");

  function t(key) {
    return (I18N[currentLang()] || I18N.en)[key] || I18N.en[key] || "";
  }

  if (form) {
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      status.className = "form-status";
      status.textContent = "";

      if (!form.checkValidity()) {
        status.classList.add("error");
        status.textContent = t("form.invalid");
        form.reportValidity();
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = t("form.sending");

      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: { Accept: "application/json" }
        });

        if (response.ok) {
          status.classList.add("success");
          status.textContent = t("form.success");
          form.reset();
        } else {
          throw new Error("Formspree responded with " + response.status);
        }
      } catch (err) {
        status.classList.add("error");
        status.textContent = t("form.error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = t("form.submit");
      }
    });
  }

  /* ---------- Gallery lightbox ---------- */
  const lightbox = document.getElementById("lightbox");

  if (lightbox) {
    const lbImg = document.getElementById("lightboxImg");
    const lbCounter = document.getElementById("lightboxCounter");
    const lbClose = document.getElementById("lightboxClose");
    const lbPrev = document.getElementById("lightboxPrev");
    const lbNext = document.getElementById("lightboxNext");
    let lbImages = [];
    let lbIndex = 0;
    let lbLastFocus = null;

    function lbRender() {
      lbImg.src = lbImages[lbIndex];
      lbCounter.textContent = (lbIndex + 1) + " / " + lbImages.length;
      const multiple = lbImages.length > 1;
      lbPrev.classList.toggle("hidden", !multiple);
      lbNext.classList.toggle("hidden", !multiple);
    }

    function lbOpen(images, opener) {
      lbImages = images;
      lbIndex = 0;
      lbLastFocus = opener;
      lbRender();
      lightbox.hidden = false;
      document.body.classList.add("lightbox-open");
      lbClose.focus();
    }

    function lbHide() {
      lightbox.hidden = true;
      document.body.classList.remove("lightbox-open");
      lbImg.src = "";
      if (lbLastFocus) lbLastFocus.focus();
    }

    function lbStep(dir) {
      if (lbImages.length < 2) return;
      lbIndex = (lbIndex + dir + lbImages.length) % lbImages.length;
      lbRender();
    }

    document.querySelectorAll(".gallery-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        const images = (btn.dataset.images || "")
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
        if (images.length) lbOpen(images, btn);
      });
    });

    lbClose.addEventListener("click", lbHide);
    lightbox.querySelector("[data-lightbox-close]").addEventListener("click", lbHide);
    lbPrev.addEventListener("click", () => lbStep(-1));
    lbNext.addEventListener("click", () => lbStep(1));

    document.addEventListener("keydown", (event) => {
      if (lightbox.hidden) return;
      if (event.key === "Escape") lbHide();
      else if (event.key === "ArrowLeft") lbStep(-1);
      else if (event.key === "ArrowRight") lbStep(1);
    });

    /* Swipe navigation on touch devices */
    let lbTouchX = null;
    lightbox.addEventListener("touchstart", (e) => {
      lbTouchX = e.changedTouches[0].clientX;
    }, { passive: true });
    lightbox.addEventListener("touchend", (e) => {
      if (lbTouchX === null) return;
      const dx = e.changedTouches[0].clientX - lbTouchX;
      if (Math.abs(dx) > 50) lbStep(dx < 0 ? 1 : -1);
      lbTouchX = null;
    }, { passive: true });
  }

  /* ---------- Cookie consent ---------- */
  const cookieBanner = document.getElementById("cookieBanner");

  if (cookieBanner) {
    const CONSENT_KEY = "dld-cookie-consent";
    let consent = null;
    try { consent = localStorage.getItem(CONSENT_KEY); } catch (e) { /* private mode */ }
    if (!consent) cookieBanner.hidden = false;

    function setConsent(value) {
      try { localStorage.setItem(CONSENT_KEY, value); } catch (e) { /* private mode */ }
      cookieBanner.hidden = true;
    }
    document.getElementById("cookieAccept").addEventListener("click", () => setConsent("accepted"));
    document.getElementById("cookieDecline").addEventListener("click", () => setConsent("declined"));
  }

  /* ---------- Footer year ---------- */
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
})();
