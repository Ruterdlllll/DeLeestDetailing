"""Screenshot the motorcycle pricing block on index, phone + desktop, NL + EN."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("qa-screenshots/moto-price")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "phone": {"width": 390, "height": 844},
    "desktop": {"width": 1920, "height": 1080},
}
PAGES = ["index.html"]

with sync_playwright() as p:
    browser = p.chromium.launch()
    for page_name in PAGES:
        for vp_name, vp in VIEWPORTS.items():
            page = browser.new_page(viewport=vp)
            page.goto(f"http://localhost:8080/{page_name}", wait_until="networkidle")
            for lang in ("nl", "en"):
                if lang == "en":
                    page.click('.lang-btn[data-lang="en"]')
                    page.wait_for_timeout(300)
                block = page.locator(".moto-price")
                block.scroll_into_view_if_needed()
                page.wait_for_timeout(700)  # let reveal animation finish
                box = block.bounding_box()
                clip = {
                    "x": max(box["x"] - 16, 0),
                    "y": max(box["y"] - 16, 0),
                    "width": min(box["width"] + 32, vp["width"]),
                    "height": box["height"] + 32,
                }
                page.screenshot(
                    path=str(OUT / f"{page_name.replace('.html', '')}-{vp_name}-{lang}.png"),
                    clip=clip,
                )
                # sanity checks
                text = block.inner_text()
                assert "€200" in text, f"missing price on {page_name}/{vp_name}/{lang}"
                expected_from = "vanaf" if lang == "nl" else "from"
                assert expected_from in text, f"missing from-prefix on {page_name}/{vp_name}/{lang}: {text!r}"
                href = block.locator("a.btn").first.get_attribute("href")
                assert href == "diensten.html#motor-detailing", f"unexpected CTA href: {href}"
            page.close()
    browser.close()
print("done")
