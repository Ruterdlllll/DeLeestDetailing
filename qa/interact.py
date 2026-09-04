"""Interaction QA for De Leest Detailing.

Tests: mobile hamburger menu, language toggle, gallery lightbox,
floating page-nav arrows, contact form validation, horizontal overflow.

Usage: .qa-venv/bin/python qa/interact.py
Output: qa-screenshots/interactions/*.png + printed PASS/FAIL report
"""
import json
import pathlib

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080"
OUT = pathlib.Path("qa-screenshots/interactions")

results = []


def report(num, name, passed, evidence):
    results.append((num, name, passed, evidence))
    print(f"[{'PASS' if passed else 'FAIL'}] {num}. {name} — {evidence}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---------- Test 1: mobile hamburger menu ----------
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True, has_touch=True, device_scale_factor=2,
        )
        page = ctx.new_page()
        page.goto(BASE, wait_until="networkidle")

        page.click("#navToggle")
        page.wait_for_timeout(500)
        nav_open = page.evaluate(
            "document.getElementById('mainNav').classList.contains('open')")
        links = page.evaluate(
            "[...document.querySelectorAll('#mainNav a')].map(a => a.textContent.trim())")
        visible = page.evaluate(
            "[...document.querySelectorAll('#mainNav a')].map(a => {"
            "const r = a.getBoundingClientRect();"
            "const s = getComputedStyle(a);"
            "return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';})")
        page.screenshot(path=str(OUT / "01-mobile-menu-open.png"))
        ok = nav_open and links == ["Diensten", "Galerij", "Over ons", "Contact", "Prijzen"] and all(visible)
        report(1, "Mobile menu opens", ok,
               f"class .open={nav_open}, links={links}, all visible={all(visible)}, "
               f"screenshot=01-mobile-menu-open.png")

        page.click('#mainNav a[href="#gallery"]')
        page.wait_for_timeout(1200)
        gal_top = page.evaluate(
            "document.getElementById('gallery').getBoundingClientRect().top")
        menu_closed = page.evaluate(
            "!document.getElementById('mainNav').classList.contains('open')")
        aria = page.evaluate("document.getElementById('navToggle').getAttribute('aria-expanded')")
        page.screenshot(path=str(OUT / "01b-mobile-after-galerij-click.png"))
        ok = gal_top >= 70 and menu_closed
        report(1, "Galerij anchor: section below header + menu closed", ok,
               f"gallery.getBoundingClientRect().top={gal_top:.1f}px (need >=70), "
               f"menu closed={menu_closed}, aria-expanded={aria}, "
               f"screenshot=01b-mobile-after-galerij-click.png")
        ctx.close()

        # ---------- Tests 2-5: desktop 1366x768 ----------
        ctx = browser.new_context(viewport={"width": 1366, "height": 768})
        page = ctx.new_page()
        page.goto(BASE, wait_until="networkidle")

        # Test 2: language toggle
        page.click('button[data-lang="en"]')
        page.wait_for_timeout(200)
        title_en = page.evaluate("document.querySelector('.hero h1').textContent.trim()")
        ok_en = title_en == "Perfection in every detail."
        page.click('button[data-lang="nl"]')
        page.wait_for_timeout(200)
        title_nl = page.evaluate("document.querySelector('.hero h1').textContent.trim()")
        ok_nl = title_nl == "Perfectie in elk detail."
        report(2, "Language toggle NL->EN->NL", ok_en and ok_nl,
               f"after EN: {title_en!r}; after NL: {title_nl!r}")

        # Test 3: gallery lightbox
        page.evaluate("document.getElementById('gallery').scrollIntoView({behavior: 'instant'})")
        page.wait_for_timeout(900)
        page.click(".gallery-item >> nth=0")
        page.wait_for_timeout(800)
        lb_open = page.evaluate("!document.getElementById('lightbox').hidden")
        img = page.evaluate("""(() => {
            const i = document.getElementById('lightboxImg');
            return {src: i.src, w: i.naturalWidth, h: i.naturalHeight};
        })()""")
        counter1 = page.evaluate("document.getElementById('lightboxCounter').textContent.trim()")
        page.screenshot(path=str(OUT / "03-lightbox-open.png"))
        ok_open = lb_open and img["w"] > 0 and counter1 == "1 / 3"
        report(3, "Lightbox opens with image + counter", ok_open,
               f"hidden={not lb_open}, counter={counter1!r}, "
               f"img natural={img['w']}x{img['h']}, src tail=...{img['src'][-60:]}, "
               f"screenshot=03-lightbox-open.png")

        page.click("#lightboxNext")
        page.wait_for_timeout(300)
        counter2 = page.evaluate("document.getElementById('lightboxCounter').textContent.trim()")
        ok_next = counter2 == "2 / 3"
        report(3, "Lightbox next button", ok_next, f"counter after #lightboxNext: {counter2!r}")

        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        lb_closed = page.evaluate("document.getElementById('lightbox').hidden")
        report(3, "Lightbox closes on Escape", lb_closed, f"hidden={lb_closed}")

        # Test 4: floating page-nav arrows
        page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
        page.wait_for_timeout(400)
        pn_display = page.evaluate("getComputedStyle(document.querySelector('.page-nav')).display")
        ok_vis = pn_display != "none"
        report(4, ".page-nav visible on desktop", ok_vis, f"display={pn_display}")

        page.click("#pageNavBottom")
        page.wait_for_timeout(1500)
        scroll = page.evaluate("""({
            y: window.scrollY,
            max: document.documentElement.scrollHeight - window.innerHeight
        })""")
        top_visible = page.evaluate(
            "!document.getElementById('pageNavTop').classList.contains('hidden')")
        near_bottom = abs(scroll["y"] - scroll["max"]) <= 30
        report(4, "pageNavBottom scrolls to bottom", near_bottom,
               f"scrollY={scroll['y']:.0f}, max={scroll['max']:.0f}, delta={abs(scroll['y'] - scroll['max']):.1f}px")
        report(4, "pageNavTop visible at bottom", top_visible,
               f".hidden removed={top_visible}")

        # Test 5: contact form validation (empty submit)
        page.evaluate("document.getElementById('contact').scrollIntoView({behavior: 'instant'})")
        page.wait_for_timeout(900)
        page.click("#contactForm button[type=submit]")
        page.wait_for_timeout(500)
        status_txt = page.evaluate("document.getElementById('formStatus').textContent.trim()")
        status_cls = page.evaluate("document.getElementById('formStatus').className")
        ok_form = status_txt.startswith("Vul alle velden in") and "error" in status_cls
        report(5, "Contact form empty-submit validation", ok_form,
               f"#formStatus text={status_txt!r}, class={status_cls!r}")
        ctx.close()

        # ---------- Test 6: horizontal overflow ----------
        for w in (320, 360, 390, 768, 1366, 1920):
            ctx = browser.new_context(viewport={"width": w, "height": 800})
            page = ctx.new_page()
            page.goto(BASE, wait_until="networkidle")
            m = page.evaluate("""({
                sw: document.documentElement.scrollWidth,
                cw: document.documentElement.clientWidth,
                iw: window.innerWidth
            })""")
            ok_w = m["sw"] <= m["iw"]
            report(6, f"No horizontal overflow @ {w}px", ok_w,
                   f"scrollWidth={m['sw']}, innerWidth={m['iw']}, clientWidth={m['cw']}, "
                   f"overflow={m['sw'] - m['iw']}px")
            ctx.close()

        browser.close()

    print("\n=== SUMMARY ===")
    print(json.dumps(
        [{"n": n, "test": t, "result": "PASS" if ok else "FAIL", "evidence": e}
         for n, t, ok, e in results],
        indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
