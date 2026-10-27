"""Verify: the Pakket/#pricing section is hidden and no link points to it or to prijzen.html.

The #pricing packages section on index.html was disabled 2026-10-28 (commented
out in the source, kept for possible restore). prijzen.html was hidden earlier
(2026-10-27). This script guards that neither is reachable from the live pages.
"""
import asyncio
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
PAGES = ["index.html", "diensten.html", "privacybeleid.html", "algemene-voorwaarden.html"]

CHECKS = []

def check(name, ok, detail=""):
    CHECKS.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f" — {detail}" if detail and not ok else ""))

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, w, h in [("desktop", 1440, 900), ("mobile", 390, 844)]:
            for path in PAGES:
                page = await browser.new_page(viewport={"width": w, "height": h})
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                await page.goto(f"{BASE}/{path}", wait_until="networkidle")
                await page.wait_for_timeout(600)

                # the #pricing section must not be present in the rendered DOM
                pricing_count = await page.evaluate(
                    "document.querySelectorAll('#pricing').length")
                check(f"[{name}] {path}: no #pricing section", pricing_count == 0,
                      f"found {pricing_count}")

                # no rendered link may point to #pricing or prijzen.html
                hrefs = await page.evaluate(
                    "[...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
                bad = [h for h in hrefs if h and ("prijzen.html" in h or "#pricing" in h)]
                check(f"[{name}] {path}: no links to pakket/prijzen", not bad, str(bad))

                check(f"[{name}] {path}: no JS errors", not errors, str(errors))
                await page.close()
        await browser.close()

    failed = [c for c in CHECKS if not c[1]]
    print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} passed")
    if failed:
        raise SystemExit(1)

asyncio.run(main())
