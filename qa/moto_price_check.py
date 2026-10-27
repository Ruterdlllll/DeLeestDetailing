"""Screenshot the Motor Detailing section on diensten.html, phone + desktop, NL + EN.

(Used to target the .moto-price band on index.html; that band is hidden along
with the #pricing section since 2026-10-28, so this now covers the motor
detailing pricing cards on diensten.html.)
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("qa-screenshots/moto-price")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "phone": {"width": 390, "height": 844},
    "desktop": {"width": 1920, "height": 1080},
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    for vp_name, vp in VIEWPORTS.items():
        page = browser.new_page(viewport=vp)
        page.goto("http://localhost:8080/diensten.html#motor-detailing",
                  wait_until="networkidle")
        for lang in ("nl", "en"):
            if lang == "en":
                page.click('.lang-btn[data-lang="en"]')
                page.wait_for_timeout(300)
            block = page.locator("#motor-detailing .pricing-grid")
            block.scroll_into_view_if_needed()
            page.wait_for_timeout(700)  # let reveal animation finish
            page.screenshot(
                path=str(OUT / f"diensten-motor-{vp_name}-{lang}.png"),
            )
            # sanity checks
            text = block.inner_text()
            for price in ("€200,-", "€250,-", "€350,-"):
                assert price in text, f"missing {price} on {vp_name}/{lang}: {text!r}"
            href = block.locator("a.btn").first.get_attribute("href")
            assert href == "index.html#contactForm", f"unexpected CTA href: {href}"
        page.close()
    browser.close()
print("done")
