"""Verify: header without contact text, contact form with phone note."""
import asyncio
from playwright.async_api import async_playwright

VIEWPORTS = [
    ("desktop", 1440, 900),
    ("ipad", 834, 1112),
    ("phone", 390, 844),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, w, h in VIEWPORTS:
            page = await browser.new_page(viewport={"width": w, "height": h})
            await page.goto("http://localhost:8080/", wait_until="networkidle")
            await page.wait_for_timeout(600)
            # header shot
            await page.screenshot(path=f"qa-screenshots/hdr-{name}.png", clip={"x": 0, "y": 0, "width": w, "height": 90})
            # contact form (NL default)
            el = page.locator(".contact-form")
            await el.scroll_into_view_if_needed()
            await page.wait_for_timeout(900)
            await el.screenshot(path=f"qa-screenshots/form-{name}-nl.png")
            if name == "desktop":
                # EN variant
                await page.click('button[data-lang="en"]')
                await page.wait_for_timeout(400)
                await el.screenshot(path=f"qa-screenshots/form-{name}-en.png")
            # header must not contain the old contact text
            hdr = await page.inner_text(".header-inner")
            assert "20781765" not in hdr, f"phone still in header on {name}"
            form = await page.inner_text(".contact-form")
            assert "20781765" in form, f"phone missing in form on {name}"
            link = await page.locator(".form-call a").get_attribute("href")
            assert link == "tel:+31620781765", link
            await page.close()
        await browser.close()
    print("OK: header clean, phone note present in form on all viewports")

asyncio.run(main())
