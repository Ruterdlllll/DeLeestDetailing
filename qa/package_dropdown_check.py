"""QA: contact-form package dropdown, preselect behaviour, about text.

The #pricing package cards on index.html are hidden (2026-10-28), so this
script only covers the contact form dropdown and its preselect logic.
"""
import asyncio
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + (" — " + detail if detail else ""))


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # --- Desktop NL: index.html ---
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(BASE + "/index.html", wait_until="networkidle")

        about = await page.inner_text("[data-i18n='about.p1']")
        check("about.p1 NL new text", "tijd die nodig is" in about and "anderen niet" not in about)

        sel = page.locator("#cf-package")
        check("package select exists", await sel.count() == 1)
        options = await sel.locator("option").all_inner_texts()
        check("dropdown options NL", options == [
            "Kies een pakket (optioneel)", "Pakket op maat", "Standard Detail",
            "Premium Detail", "Ceramic Package", "Motor Detailing"], str(options))

        # EN toggle
        await page.locator(".lang-btn[data-lang='en']").first.click()
        await page.wait_for_timeout(200)
        options_en = await sel.locator("option").all_inner_texts()
        check("dropdown options EN", options_en[0] == "Choose a package (optional)"
              and "Custom Package" in options_en and "Motorcycle Detailing" in options_en, str(options_en))
        about_en = await page.inner_text("[data-i18n='about.p1']")
        check("about.p1 EN new text", "time it takes" in about_en and "others won't" not in about_en)
        await page.close()

        # --- Query param preselect ---
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(BASE + "/index.html?package=ceramic#contactForm", wait_until="networkidle")
        check("?package=ceramic preselects", await page.locator("#cf-package").input_value() == "ceramic")
        await page.close()

        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(BASE + "/index.html?package=bogus#contactForm", wait_until="networkidle")
        check("bogus package ignored", await page.locator("#cf-package").input_value() == "")
        await page.close()

        # --- Mobile: form renders, dropdown usable ---
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        await page.goto(BASE + "/index.html?package=premium#contactForm", wait_until="networkidle")
        check("mobile preselect premium", await page.locator("#cf-package").input_value() == "premium")
        await page.locator("#contactForm").screenshot(path="qa-screenshots/form-mobile.png")
        await page.close()

        await browser.close()

    failed = [c for c in CHECKS if not c[1]]
    print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} passed")
    if failed:
        raise SystemExit(1)


asyncio.run(main())
