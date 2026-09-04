"""Ad-hoc QA: mobile footer Instagram alignment + privacybeleid.html in nl/en."""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path("qa-screenshots/privacy-footer-check")
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://localhost:8080"

with sync_playwright() as p:
    # Mobile footer check on the homepage (iPhone SE)
    iphone = p.devices["iPhone SE"]
    b = p.chromium.launch()
    ctx = b.new_context(**iphone, locale="nl-NL")
    page = ctx.new_page()
    page.goto(f"{BASE}/index.html")
    page.evaluate("localStorage.setItem('dld-cookie-consent','accepted')")
    page.reload()
    footer = page.locator(".site-footer")
    footer.scroll_into_view_if_needed()
    footer.screenshot(path=str(OUT / "mobile-footer-nl.png"))

    # Privacy page: mobile NL + EN, desktop NL + EN
    for lang in ("nl", "en"):
        page.goto(f"{BASE}/privacybeleid.html")
        page.evaluate(f"localStorage.setItem('dld-lang','{lang}')")
        page.reload()
        page.screenshot(path=str(OUT / f"privacy-mobile-{lang}.png"), full_page=True)
    ctx.close()

    ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="nl-NL")
    page = ctx.new_page()
    for lang in ("nl", "en"):
        page.goto(f"{BASE}/privacybeleid.html")
        page.evaluate(f"localStorage.setItem('dld-lang','{lang}')")
        page.reload()
        page.screenshot(path=str(OUT / f"privacy-desktop-{lang}.png"), full_page=True)
    # Desktop footer (link row) for reference
    page.goto(f"{BASE}/index.html")
    page.evaluate("localStorage.setItem('dld-cookie-consent','accepted')")
    page.reload()
    footer = page.locator(".site-footer")
    footer.scroll_into_view_if_needed()
    footer.screenshot(path=str(OUT / "desktop-footer-nl.png"))
    ctx.close()
    b.close()

print("DONE", sorted(f.name for f in OUT.glob("*.png")))
