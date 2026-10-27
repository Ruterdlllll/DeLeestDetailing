"""Verify: index.html #pricing prices render, and no link points to prijzen.html."""
import asyncio
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"

CHECKS = []

def check(name, ok, detail=""):
    CHECKS.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f" — {detail}" if detail and not ok else ""))

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, w, h in [("desktop", 1440, 900), ("mobile", 390, 844)]:
            page = await browser.new_page(viewport={"width": w, "height": h})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            await page.goto(f"{BASE}/index.html", wait_until="networkidle")
            await page.wait_for_timeout(600)

            # prices in the index.html #pricing section
            prices = await page.evaluate(
                "[...document.querySelectorAll('#pricing .price-value')].map(e => e.textContent)")
            print(f"[{name}] index.html #pricing prices: {prices}")
            check(f"[{name}] #pricing prices", prices == [
                "€199", "€399", "Prijs op aanvraag", "Prijs op aanvraag", "€200"], str(prices))
            froms = await page.evaluate(
                "[...document.querySelectorAll('#pricing .price-from')].map(e => e.textContent)")
            check(f"[{name}] vanaf prefixes", froms == ["vanaf", "vanaf", "vanaf"], str(froms))
            note = await page.text_content("#pricing .pricing-note")
            check(f"[{name}] pricing note mentions btw", note is not None and "btw" in note.lower(),
                  str(note))

            # no link anywhere on index.html may point to prijzen.html
            hrefs = await page.evaluate(
                "[...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
            bad = [h for h in hrefs if h and "prijzen.html" in h]
            check(f"[{name}] no link to prijzen.html", not bad, str(bad))

            check(f"[{name}] no JS errors", not errors, str(errors))
            await page.screenshot(path=f"qa-screenshots/anchor_{name}.png")
            await page.close()
        await browser.close()

    failed = [c for c in CHECKS if not c[1]]
    print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} passed")
    if failed:
        raise SystemExit(1)

asyncio.run(main())
