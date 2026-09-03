"""Verify: #vergelijken anchor lands on the comparison table, new prices render."""
import asyncio
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, w, h in [("desktop", 1440, 900), ("mobile", 390, 844)]:
            page = await browser.new_page(viewport={"width": w, "height": h})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            await page.goto(f"{BASE}/prijzen.html#vergelijken", wait_until="networkidle")
            await page.wait_for_timeout(1200)
            tbl_top = await page.evaluate(
                "document.querySelector('#vergelijken').getBoundingClientRect().top")
            header_h = await page.evaluate(
                "document.querySelector('.site-header').getBoundingClientRect().height")
            print(f"[{name}] #vergelijken top={tbl_top:.0f}px, header={header_h:.0f}px")
            assert tbl_top >= header_h - 5, "section hidden under fixed header!"
            await page.screenshot(path=f"qa-screenshots/anchor_{name}.png")
            assert not errors, errors

            # prices on prijzen.html
            prices = await page.evaluate(
                "[...document.querySelectorAll('.price-value')].map(e => e.textContent)")
            print(f"[{name}] prijzen.html prices: {prices}")
            assert prices[:3] == ["€199", "€299", "€599"], prices
            note = await page.text_content(".pricing-note")
            assert "inclusief btw" in note, note
            await page.close()

            # prices on index.html + compare CTA href
            page = await browser.new_page(viewport={"width": w, "height": h})
            await page.goto(f"{BASE}/index.html", wait_until="networkidle")
            prices = await page.evaluate(
                "[...document.querySelectorAll('.price-value')].map(e => e.textContent)")
            print(f"[{name}] index.html prices: {prices}")
            assert prices[:3] == ["€199", "€299", "€599"], prices
            href = await page.get_attribute(
                "a[data-i18n='pricing.compareCta']", "href")
            print(f"[{name}] compare CTA href: {href}")
            assert href == "prijzen.html#vergelijken", href
            await page.close()
        await browser.close()
        print("ALL CHECKS PASSED")

asyncio.run(main())
