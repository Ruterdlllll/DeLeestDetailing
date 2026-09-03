"""Screenshot the header language toggle on phone and desktop viewports."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("qa-screenshots/lang-toggle")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "phone": {"width": 390, "height": 844},
    "desktop": {"width": 1920, "height": 1080},
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    for name, vp in VIEWPORTS.items():
        page = browser.new_page(viewport=vp)
        page.goto("http://localhost:8000/index.html", wait_until="networkidle")
        toggle = page.locator(".lang-toggle")
        toggle.scroll_into_view_if_needed()
        box = toggle.bounding_box()
        print(name, "lang-toggle box:", box)
        # generous crop around the toggle so we can judge spacing/visibility
        clip = {
            "x": max(box["x"] - 60, 0),
            "y": max(box["y"] - 30, 0),
            "width": box["width"] + 120,
            "height": box["height"] + 60,
        }
        page.screenshot(path=str(OUT / f"{name}.png"), clip=clip)
        page.close()
    browser.close()
print("done")
