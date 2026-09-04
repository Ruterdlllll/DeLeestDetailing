import asyncio
from playwright.async_api import async_playwright

VIEWPORTS = [(1440, 900, "desktop"), (390, 844, "phone")]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for w, h, name in VIEWPORTS:
            page = await browser.new_page(viewport={"width": w, "height": h})
            await page.goto("http://localhost:8080/", wait_until="networkidle")
            for lang in ("nl", "en"):
                if lang == "en":
                    await page.click('button[data-lang="en"]')
                    await page.wait_for_timeout(300)
                await page.locator("#contact").scroll_into_view_if_needed()
                await page.wait_for_timeout(900)
                el = page.locator(".contact-body")
                await el.screenshot(path=f"qa-screenshots/visit-{name}-{lang}.png")
                body = await el.inner_text()
                checks = {
                    "nl": ["Vind ons", "Adres", "Molenstraat 44, 5737 BW Lieshout",
                           "+31 (0)6 20781765", "info@deleestdetailing.nl",
                           "Bekijk de route op Google Maps"],
                    "en": ["Find us", "Address", "Molenstraat 44, 5737 BW Lieshout",
                           "+31 (0)6 20781765", "info@deleestdetailing.nl",
                           "View route on Google Maps"],
                }[lang]
                missing = [c for c in checks if c not in body]
                href = await page.locator(".maps-link").get_attribute("href")
                print(f"{name}/{lang}: {'OK' if not missing else 'MISSING: ' + str(missing)} | maps href: {href}")
            await page.close()
        # privacy + terms pages: placeholders filled
        for url in ("privacybeleid.html", "algemene-voorwaarden.html"):
            page = await browser.new_page()
            await page.goto(f"http://localhost:8080/{url}", wait_until="networkidle")
            body = await page.locator("body").inner_text()
            bad = [t for t in ("[STRAAT", "[KVK-NUMMER]", "[E-MAILADRES]", "[STREET", "[COC NUMBER]", "[EMAIL ADDRESS]") if t in body]
            ok = all(t in body for t in ("Molenstraat 44", "86191365", "info@deleestdetailing.nl"))
            print(f"{url}: {'OK' if ok and not bad else 'PROBLEM leftover=' + str(bad) + ' filled=' + str(ok)}")
            await page.close()
        await browser.close()

asyncio.run(main())
