"""Verify contact-CTA anchors land on the form, and ceramic price on request.

Usage: .qa-venv/bin/python qa/contact_anchor_check.py  (server on :8080)
Output: qa-screenshots/anchor-check/*.png
"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080"
OUT = pathlib.Path("qa-screenshots/anchor-check")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "phone":   {"width": 390, "height": 844, "mobile": True},
    "desktop": {"width": 1920, "height": 1080, "mobile": False},
}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for dev, cfg in VIEWPORTS.items():
            ctx = browser.new_context(
                viewport={"width": cfg["width"], "height": cfg["height"]},
                is_mobile=cfg["mobile"],
                has_touch=cfg["mobile"],
                device_scale_factor=2 if cfg["mobile"] else 1,
            )

            # 1) Package CTA on index -> should land on the contact form
            page = ctx.new_page()
            page.goto(f"{BASE}/index.html", wait_until="networkidle")
            page.locator("#pricing .price-card").first.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            page.locator("#pricing .price-card .btn").first.click()
            page.wait_for_timeout(1200)  # smooth scroll
            box = page.locator("#contactForm").bounding_box()
            print(f"{dev}: form top after CTA click = {box['y']:.0f}px")
            page.screenshot(path=str(OUT / f"{dev}-index-cta.png"))

            # 2) Cross-page link from prijzen.html -> index.html#contactForm
            page.goto(f"{BASE}/prijzen.html", wait_until="networkidle")
            page.locator(".price-card .btn").first.click()
            page.wait_for_timeout(1800)
            box = page.locator("#contactForm").bounding_box()
            print(f"{dev}: form top from prijzen.html = {box['y']:.0f}px")
            page.screenshot(path=str(OUT / f"{dev}-prijzen-cta.png"))

            # 3) Ceramic card shows "price on request" (NL + EN)
            page.goto(f"{BASE}/prijzen.html", wait_until="networkidle")
            card = page.locator(".price-card").nth(3)
            card.scroll_into_view_if_needed()
            page.wait_for_timeout(600)
            card.screenshot(path=str(OUT / f"{dev}-ceramic-nl.png"))
            page.click('button[data-lang="en"]')
            page.wait_for_timeout(400)
            card.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            card.screenshot(path=str(OUT / f"{dev}-ceramic-en.png"))
            print(f"{dev}: ceramic EN price text = "
                  f"{card.locator('.price-value').inner_text()!r}")
            page.close()
            ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
