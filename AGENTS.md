# AGENTS.md — De Leest Detailing

## Project overview

Static marketing website for **De Leest Detailing**, a premium car & motorcycle
detailing business. There is **no build step, no framework, no package manager** —
just plain HTML, CSS and vanilla JavaScript served as-is. The site is bilingual
(NL is the default language, EN is a toggle) and is deployed to GitHub Pages.

- Live domain: `deleestdetailing.nl` (see `CNAME`).
- Contact form posts to Formspree (`https://formspree.io/f/xkjnjdzb`, submitted
  via `fetch` in `js/main.js`).
- Only third-party runtime dependencies: Google Fonts (Sora + Inter), Unsplash
  images, Formspree. No cookies are set beyond a `localStorage` consent flag.

## Working rules

- This folder (`/run/media/system/Games/Kimi/Website Car Detailing/`) is the
  **only** working folder for this project. Do not work from or serve any other
  directory.
- Do **not** start other services, dev servers, or localhost instances. If a
  local server is needed, ask the user first.
- Exception approved by the user: one `python3 -m http.server 8080
  --bind 127.0.0.1` serving this folder may be kept running; do not kill it
  and do not start additional servers on other ports.

## Repository layout

```
index.html                  Homepage (hero, services, gallery, about, contact form, pricing teaser)
prijzen.html                Pricing page (packages & price tables)
algemene-voorwaarden.html   Terms & conditions (Dutch only, robots noindex)
css/style.css               Single stylesheet, dark premium theme, CSS custom properties in :root
js/i18n.js                  I18N dictionary: en + nl translations, keys match data-i18n attributes
js/main.js                  All interactions (IIFE, "use strict", no imports/exports)
assets/                     favicon.svg, whatsapp-profile.png
qa/                         Python/Playwright QA scripts (not shipped, see .gitignore for venv)
qa-screenshots/             QA screenshot output (gitignored)
.qa-venv/                   Local Python venv with Playwright (gitignored)
.github/workflows/static.yml  GitHub Pages deploy workflow
CNAME                       Custom domain for GitHub Pages
```

## Code conventions

- **No build tooling.** Edit HTML/CSS/JS directly; what you save is what ships.
  Do not introduce bundlers, preprocessors, or npm.
- **i18n is data-driven.** Every user-facing string on `index.html` and
  `prijzen.html` goes through `data-i18n="key"` (plus `data-i18n-placeholder`
  and `data-i18n-aria` variants). Translations live in `js/i18n.js` under
  `I18N.en` and `I18N.nl` — **when adding or changing a string, update both
  languages** and use the same dotted key. The selected language is persisted
  in `localStorage` under `dld-lang`; NL is the default.
- `js/main.js` is one IIFE organised in banner-comment sections
  (`/* ---------- Section ---------- */`). It handles: language toggle, sticky
  header + floating page-nav arrows, mobile hamburger menu, scroll-reveal
  (`IntersectionObserver`, `.reveal` → `.visible`), the Formspree contact form,
  gallery lightbox (keyboard + touch swipe), cookie-consent banner, footer year.
  New behaviour goes in a new labelled section in this file.
- CSS uses custom properties from `:root` (`--bg`, `--accent`, `--radius`, …) —
  reuse them instead of hardcoding colours. Fonts are `--font-head` (Sora) and
  `--font-body` (Inter).
- Accessibility matters: `prefers-reduced-motion` is respected for smooth
  scrolling, the lightbox manages focus and arrow keys, nav toggle keeps
  `aria-expanded` in sync. Preserve these behaviours when editing.
- Code comments and documentation are in English; visible site copy is NL/EN.
- Known placeholder: header social links still have `href="#"` with a TODO
  comment — replace with real profile URLs when they exist.

## Running locally

```bash
python3 -m http.server 8080 --bind 127.0.0.1
# open http://localhost:8080/index.html
```

The standard local entry page is `index.html` (http://localhost:8080/index.html) —
not `prijzen.html`. (Ask the user before starting any server — see Working
rules. If the approved 8080 server is already running, reuse it.)

## Testing / QA

There is no unit-test suite. QA is done with **Playwright (Python)** scripts in
`qa/`, run from the gitignored `.qa-venv/` virtualenv against the site served on
`http://localhost:8080`:

```bash
python3 -m http.server 8080 --bind 127.0.0.1 &   # serve the site first
.qa-venv/bin/python qa/shoot.py        # full screenshot matrix: 6 devices × nl/en × all sections
.qa-venv/bin/python qa/interact.py     # interactive checks with printed PASS/FAIL report
```

- `qa/shoot.py` — screenshots every section per device (iPhone SE/14, Android,
  iPad, laptop, desktop) in both languages, plus a full-page capture, into
  `qa-screenshots/<device>/<lang>/`.
- `qa/interact.py` — tests hamburger menu, language toggle, lightbox,
  page-nav arrows, form validation, horizontal overflow.
- The other `qa/*_check.py` scripts are ad-hoc visual checks for specific fixes
  (header, language toggle, opening hours, price tables, anchors, gaps) that
  save screenshots under `qa-screenshots/`.

Visual verification is the norm: after changing layout or styling, run the
relevant QA script and inspect the PNGs. Reveal animations are triggered by
scrolling, so full-page screenshots must scroll down in steps first (see
`shoot.py` for the pattern).

## Deployment

Push to `main` triggers `.github/workflows/static.yml`, which uploads the
**entire repository** as the GitHub Pages artifact and deploys it. Deployment
is fully automatic — there is nothing to build. Keep the `CNAME` file intact.

## Security considerations

- No secrets, no backend, no build tokens — the only external POST target is
  the public Formspree endpoint.
- The cookie-consent banner stores only a `localStorage` flag
  (`dld-cookie-consent`); no tracking is loaded.
- `localStorage` access is wrapped in try/catch for private browsing; keep that
  pattern when touching storage.
