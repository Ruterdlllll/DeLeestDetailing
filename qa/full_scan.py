"""Full-site QA scan: console errors, failed requests, screenshots.

Covers index.html, prijzen.html, algemene-voorwaarden.html
x (desktop, mobile) x (NL, EN). Reports JS console errors, page errors
and failed network requests, then saves full-page screenshots.

Usage: .qa-venv/bin/python qa/full_scan.py
Output: qa-screenshots/scan/<page>-<device>-<lang>.png
"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080"
PAGES = ["index.html", "prijzen.html", "algemene-voorwaarden.html"]
OUT = pathlib.Path("qa-screenshots/scan")

VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080, "mobile": False},
    "mobile": {"width": 390, "height": 844, "mobile": True},
}

problems = []


def settle(page):
    # scroll down in steps so .reveal elements and lazy images show up
    page.evaluate("""() => {
        return new Promise(resolve => {
            let y = 0;
            const step = () => {
                window.scrollTo({top: y, behavior: 'instant'});
                y += window.innerHeight * 0.7;
                if (y < document.body.scrollHeight) { setTimeout(step, 120); }
                else { window.scrollTo({top: 0, behavior: 'instant'}); resolve(); }
            };
            step();
        });
    }""")
    page.wait_for_timeout(800)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for pg in PAGES:
            for dev, cfg in VIEWPORTS.items():
                for lang in ("nl", "en"):
                    ctx = browser.new_context(
                        viewport={"width": cfg["width"], "height": cfg["height"]},
                        is_mobile=cfg["mobile"],
                        has_touch=cfg["mobile"],
                        device_scale_factor=2 if cfg["mobile"] else 1,
                    )
                    page = ctx.new_page()
                    tag = f"{pg} [{dev}/{lang}]"
                    page.on("console", lambda m, t=tag: problems.append(f"{t} console.{m.type}: {m.text}")
                            if m.type in ("error", "warning") else None)
                    page.on("pageerror", lambda e, t=tag: problems.append(f"{t} pageerror: {e}"))
                    page.on("requestfailed", lambda r, t=tag: problems.append(
                        f"{t} requestfailed: {r.url} ({r.failure})"))
                    page.on("response", lambda r, t=tag: problems.append(f"{t} HTTP {r.status}: {r.url}")
                            if r.status >= 400 else None)

                    page.goto(f"{BASE}/{pg}", wait_until="networkidle")
                    if lang == "en":
                        btn = page.query_selector('button[data-lang="en"]')
                        if btn:
                            btn.click()
                            page.wait_for_timeout(300)
                        else:
                            problems.append(f"{tag} NO language toggle found")
                    settle(page)

                    OUT.mkdir(parents=True, exist_ok=True)
                    name = f"{pg.replace('.html','')}-{dev}-{lang}.png"
                    page.screenshot(path=str(OUT / name), full_page=True)

                    # horizontal overflow check
                    overflow = page.evaluate(
                        "document.documentElement.scrollWidth - document.documentElement.clientWidth")
                    if overflow > 1:
                        problems.append(f"{tag} horizontal overflow: {overflow}px")
                    ctx.close()
                    print(f"done {tag}")
        browser.close()

    print("\n=== PROBLEMS ===")
    if problems:
        for p_ in problems:
            print(p_)
    else:
        print("none")


if __name__ == "__main__":
    main()
