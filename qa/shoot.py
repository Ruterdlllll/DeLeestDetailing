"""Screenshot loop for De Leest Detailing QA.

Shoots every page section (hero, services, gallery, about, contact, footer)
plus a full-page capture, across a matrix of device sizes, in NL and EN.

Usage: .qa-venv/bin/python qa/shoot.py
Output: qa-screenshots/<device>/<lang>/<section>.png
"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000"
OUT = pathlib.Path("qa-screenshots")

DEVICES = {
    "iphone-se":   {"width": 375,  "height": 667,  "mobile": True},
    "iphone-14":   {"width": 390,  "height": 844,  "mobile": True},
    "android":     {"width": 360,  "height": 800,  "mobile": True},
    "ipad":        {"width": 768,  "height": 1024, "mobile": True},
    "laptop":      {"width": 1366, "height": 768,  "mobile": False},
    "desktop":     {"width": 1920, "height": 1080, "mobile": False},
}

SECTIONS = ["hero", "services", "gallery", "about", "contact", "footer"]


def scroll_to_section(page, section):
    if section == "hero":
        page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
    elif section == "footer":
        page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'instant'})")
    else:
        page.evaluate(
            "document.getElementById('%s').scrollIntoView({behavior: 'instant'})" % section
        )
    # let reveal animations and lazy images settle
    page.wait_for_timeout(900)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for dev, cfg in DEVICES.items():
            for lang in ("nl", "en"):
                ctx = browser.new_context(
                    viewport={"width": cfg["width"], "height": cfg["height"]},
                    is_mobile=cfg["mobile"],
                    has_touch=cfg["mobile"],
                    device_scale_factor=2 if cfg["mobile"] else 1,
                )
                page = ctx.new_page()
                page.goto(BASE, wait_until="networkidle")
                if lang == "en":
                    page.click('button[data-lang="en"]')
                    page.wait_for_timeout(300)

                outdir = OUT / dev / lang
                outdir.mkdir(parents=True, exist_ok=True)

                for section in SECTIONS:
                    scroll_to_section(page, section)
                    page.screenshot(path=str(outdir / f"{section}.png"))

                # full page as one tall image for layout review; scroll down
                # in steps first so every .reveal element becomes visible
                page.evaluate("""() => {
                    return new Promise(resolve => {
                        let y = 0;
                        const step = () => {
                            window.scrollTo({top: y, behavior: 'instant'});
                            y += window.innerHeight * 0.7;
                            if (y < document.body.scrollHeight) { setTimeout(step, 120); }
                            else { resolve(); }
                        };
                        step();
                    });
                }""")
                page.wait_for_timeout(800)
                scroll_to_section(page, "hero")
                page.screenshot(path=str(outdir / "full.png"), full_page=True)
                ctx.close()
                print(f"done {dev}/{lang}")
        browser.close()


if __name__ == "__main__":
    main()
