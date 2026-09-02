import asyncio
from playwright.async_api import async_playwright

VIEWPORTS = [(1440, 900, "desktop"), (834, 1112, "ipad"), (390, 844, "phone")]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for w, h, name in VIEWPORTS:
            page = await browser.new_page(viewport={"width": w, "height": h})
            await page.goto("http://localhost:8000/", wait_until="networkidle")
            for lang in ("nl", "en"):
                if lang == "en":
                    await page.click('button[data-lang="en"]')
                    await page.wait_for_timeout(300)
                await page.locator("#contact").scroll_into_view_if_needed()
                await page.wait_for_timeout(900)  # let reveals finish
                el = page.locator(".contact-body")
                await el.screenshot(path=f"qa-screenshots/hours-{name}-{lang}.png")
                # text checks
                body = await page.locator(".contact-body").inner_text()
                checks = {
                    "nl": ["Openingstijden", "Maandag t/m vrijdag", "08:30", "Op afspraak", "Gesloten"],
                    "en": ["Opening hours", "Monday – Friday", "08:30", "By appointment", "Closed"],
                }[lang]
                missing = [c for c in checks if c not in body]
                print(f"{name}/{lang}: {'OK' if not missing else 'MISSING: ' + str(missing)}")
            await page.close()
        await browser.close()

asyncio.run(main())
