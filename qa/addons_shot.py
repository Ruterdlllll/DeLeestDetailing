"""One-off: screenshot the changed addon areas on diensten.html (desktop + mobile)."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
OUT = Path("qa-screenshots/diensten")
OUT.mkdir(parents=True, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, vw in (("desktop", {"width": 1440, "height": 900}),
                         ("mobile", {"width": 390, "height": 844})):
            page = await browser.new_page(viewport=vw)
            await page.goto(f"{BASE}/diensten.html", wait_until="networkidle")
            await page.evaluate("document.querySelector('.cookie-banner')?.remove()")
            for anchor in ("interieur-reinigen", "polijsten",
                           "keramische-coating", "motor-detailing"):
                el = page.locator(f"section#{anchor} .svc-addons")
                await el.scroll_into_view_if_needed()
                await page.wait_for_timeout(700)
                await el.screenshot(path=str(OUT / f"addons-{anchor}-{name}.png"))
            # nav header check for the Pakket rename
            hdr = page.locator(".site-header")
            await page.evaluate("window.scrollTo(0,0)")
            await page.wait_for_timeout(300)
            await hdr.screenshot(path=str(OUT / f"header-{name}.png"))
            await page.close()
        await browser.close()
    print("done")

asyncio.run(main())
