"""QA: package dropdown, preselect behaviour, std card texts, about text."""
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

        # std card features (strict: card whose h3 is pkg.std.name)
        card = page.locator(".price-card", has=page.locator("h3[data-i18n='pkg.std.name']"))
        feats = await card.locator(".price-features span").all_inner_texts()
        check("std card NL features", "Wax aanbrengen" in feats and "Banden dressen" in feats
              and "Dashboard & console reinigen" in feats
              and "Clay bar behandeling" not in feats and "Paint sealant" not in feats, str(feats))

        # premium card gained clay bar
        prem = page.locator(".price-card", has=page.locator("h3[data-i18n='pkg.premium.name']"))
        prem_feats = await prem.locator(".price-features span").all_inner_texts()
        check("premium card NL has clay bar", "Clay bar behandeling" in prem_feats, str(prem_feats))

        # ceramic card gained glass coating
        cer = page.locator(".price-card", has=page.locator("h3[data-i18n='pkg.ceramic.name']"))
        cer_feats = await cer.locator(".price-features span").all_inner_texts()
        check("ceramic card NL has glass coating", "Glascoating" in cer_feats, str(cer_feats))

        # click premium "Boek dit pakket" -> select = premium
        await card.page.locator(".price-card-featured a[data-package]").click()
        await page.wait_for_timeout(300)
        check("click premium -> select premium", await sel.input_value() == "premium")

        # moto band links to the motor detailing section on diensten.html
        moto_href = await page.locator(".moto-price a.btn").get_attribute("href")
        check("moto band links to diensten.html#motor-detailing",
              moto_href == "diensten.html#motor-detailing", str(moto_href))

        # EN toggle
        await page.locator(".lang-btn[data-lang='en']").first.click()
        await page.wait_for_timeout(200)
        options_en = await sel.locator("option").all_inner_texts()
        check("dropdown options EN", options_en[0] == "Choose a package (optional)"
              and "Custom Package" in options_en and "Motorcycle Detailing" in options_en, str(options_en))
        about_en = await page.inner_text("[data-i18n='about.p1']")
        check("about.p1 EN new text", "time it takes" in about_en and "others won't" not in about_en)
        feats_en = await card.locator(".price-features span").all_inner_texts()
        check("std card EN features", "Wax application" in feats_en and "Tyre dressing" in feats_en
              and "Clay bar treatment" not in feats_en and "Paint sealant" not in feats_en, str(feats_en))
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
