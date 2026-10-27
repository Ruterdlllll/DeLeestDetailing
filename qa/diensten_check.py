"""QA for diensten.html and the services nav dropdown.

Checks:
- dropdown present on all 5 pages with 8 service links in 3 groups
- diensten.html: 8 anchored sections with their exact prices
- no competitor brand names / excluded services in markup
- NL/EN toggle swaps section text
- desktop hover opens the dropdown; mobile tap toggles it
- screenshots to qa-screenshots/diensten/
"""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
OUT = Path("qa-screenshots/diensten")
OUT.mkdir(parents=True, exist_ok=True)

PAGES = ["index.html", "prijzen.html", "diensten.html",
         "privacybeleid.html", "algemene-voorwaarden.html"]

ANCHORS = ["interieur-reinigen", "vlekken-verwijderen", "handwassen",
           "polijsten", "keramische-coating", "cabrio-dak",
           "motor-detailing", "lakdiktemeting"]

GROUPS = ["Interieur", "Exterieur", "Aanvullend"]

SECTION_PRICES = {
    "interieur-reinigen": ["€125", "€185", "€295", "+ €50"],
    "vlekken-verwijderen": ["€60", "€160"],
    "handwassen": ["€95", "€145", "€185", "+ €50"],
    "polijsten": ["€295", "€395", "€595", "+ €55", "+ €95", "+ €150"],
    "keramische-coating": ["€895", "€995", "+ €200", "+ €350", "€85"],
    "cabrio-dak": ["€175", "€275"],
    "motor-detailing": ["€200", "€250", "€350"],
    "lakdiktemeting": ["€19,95", "€29,95"],
}

FORBIDDEN = ["KRYTEX", "Krytex", "Labocosmetica", "labocosmetica",
             "Cartec", "Jetski", "jetski", "Embleem", "embleem",
             "ozon", "Ozon", "parfum", "Parfum", "Lakverzegeling",
             "lakverzegeling", "Helm &amp; Vizier", "Screen Coating",
             "polijsten glansherstel", "fluorvr", "Raam Sealant",
             "Raam Coating", "Leer verzorgen", "Keramische Coating Basic",
             "Keramische Coating Premium"]

CHECKS = []

def check(name, ok, detail=""):
    CHECKS.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f" — {detail}" if detail and not ok else ""))

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # --- Dropdown structure on every page ---
        for page_name in PAGES:
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            await page.goto(f"{BASE}/{page_name}", wait_until="networkidle")
            links = await page.locator(".nav-dropdown-panel a").evaluate_all(
                "els => els.map(e => e.getAttribute('href'))")
            expected = ["diensten.html"] + [f"diensten.html#{a}" for a in ANCHORS]
            check(f"{page_name}: dropdown has 8 service links + overview",
                  links == expected, str(links))
            groups = await page.locator(".nav-dropdown-group").all_text_contents()
            groups = [g.strip() for g in groups]
            check(f"{page_name}: 3 dropdown groups", groups == GROUPS, str(groups))
            check(f"{page_name}: no JS errors", not errors, str(errors))
            await page.close()

        # --- diensten.html sections & prices ---
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(f"{BASE}/diensten.html", wait_until="networkidle")
        for anchor in ANCHORS:
            count = await page.locator(f"section#{anchor}").count()
            check(f"section #{anchor} exists", count == 1)
            if count != 1:
                continue
            text = await page.locator(f"section#{anchor}").inner_text()
            missing = [pr for pr in SECTION_PRICES[anchor] if pr not in text]
            check(f"#{anchor} prices {SECTION_PRICES[anchor]}", not missing,
                  f"missing: {missing}")
        body = await page.inner_text("body")
        found = [f for f in FORBIDDEN if f in body]
        check("no competitor brands / excluded services", not found, str(found))
        html = await page.content()
        found_html = [f for f in FORBIDDEN if f in html]
        check("no forbidden strings in raw HTML", not found_html, str(found_html))
        # footer note present on interieur (VAT note)
        interieur = await page.locator("section#interieur-reinigen").inner_text()
        check("interieur has btw footnote", "btw" in interieur.lower())
        # CTA links point at the contact form
        cta_hrefs = await page.locator(".svc-cta a, .svc-grid a.btn").evaluate_all(
            "els => els.map(e => e.getAttribute('href'))")
        bad = [h for h in cta_hrefs if "index.html#contactForm" not in (h or "")]
        check("service CTAs point to contact form", not bad, str(bad))

        # --- EN toggle swaps section text ---
        h2_nl = await page.locator("section#interieur-reinigen h2").inner_text()
        await page.locator(".lang-btn[data-lang='en']").first.click()
        await page.wait_for_timeout(300)
        h2_en = await page.locator("section#interieur-reinigen h2").inner_text()
        check("NL/EN toggle swaps section title", h2_nl != h2_en,
              f"nl={h2_nl!r} en={h2_en!r}")
        await page.locator(".lang-btn[data-lang='nl']").first.click()
        await page.wait_for_timeout(200)

        # --- Desktop: hover opens dropdown ---
        await page.goto(f"{BASE}/index.html", wait_until="networkidle")
        await page.locator(".nav-dropdown-toggle").hover()
        await page.wait_for_timeout(400)
        visible = await page.locator(".nav-dropdown-panel").is_visible()
        check("desktop hover opens dropdown", visible)
        await page.screenshot(path=str(OUT / "dropdown-desktop.png"))
        # anchor navigation: click Lakdiktemeting in the panel
        await page.locator(".nav-dropdown-panel a[href='diensten.html#lakdiktemeting']").click()
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(600)
        check("dropdown link navigates to anchor",
              page.url.endswith("diensten.html#lakdiktemeting"), page.url)
        top = await page.evaluate(
            "document.querySelector('#lakdiktemeting').getBoundingClientRect().top")
        check("anchor not hidden under sticky header", top >= 60, f"top={top}")
        await page.close()

        # --- Mobile: tap toggles dropdown ---
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        await page.goto(f"{BASE}/index.html", wait_until="networkidle")
        await page.click("#navToggle")
        await page.wait_for_timeout(400)
        hidden_before = await page.evaluate(
            "getComputedStyle(document.querySelector('.nav-dropdown-panel')).display === 'none'")
        check("mobile: panel hidden before tap", hidden_before)
        await page.locator(".nav-dropdown-toggle").click()
        await page.wait_for_timeout(300)
        shown = await page.evaluate(
            "getComputedStyle(document.querySelector('.nav-dropdown-panel')).display !== 'none'")
        aria = await page.locator(".nav-dropdown-toggle").get_attribute("aria-expanded")
        check("mobile: tap opens panel + aria-expanded", shown and aria == "true",
              f"shown={shown} aria={aria}")
        await page.screenshot(path=str(OUT / "dropdown-mobile-open.png"))
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(200)
        closed = await page.evaluate(
            "getComputedStyle(document.querySelector('.nav-dropdown-panel')).display === 'none'")
        check("mobile: ESC closes panel", closed)
        await page.close()

        # --- Screenshots of two sections (desktop) ---
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(f"{BASE}/diensten.html", wait_until="networkidle")
        for anchor in ("handwassen", "motor-detailing"):
            el = page.locator(f"section#{anchor}")
            await el.scroll_into_view_if_needed()
            await page.wait_for_timeout(700)
            await el.screenshot(path=str(OUT / f"section-{anchor}.png"))
        await page.close()

        await browser.close()

    failed = [c for c in CHECKS if not c[1]]
    print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} passed")
    if failed:
        raise SystemExit(1)

asyncio.run(main())
