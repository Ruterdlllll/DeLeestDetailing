"""Verify all photos load from local assets and render correctly.

Checks (desktop 1440px + mobile 390px, NL):
- no failed image requests (>= 400) and no external image requests
- every <img> on index.html has naturalWidth > 0
- lightbox opens on a gallery tile and steps through its 3 photos
Screenshots: hero, services, gallery, about, lightbox -> qa-screenshots/local-images/
"""
import os
import shutil
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080"
OUT = "qa-screenshots/local-images"

failures = []


def check_page(page, label):
    bad_requests = []
    external_images = []

    def on_response(resp):
        if resp.status >= 400:
            bad_requests.append(f"{resp.status} {resp.url}")
        if resp.request.resource_type == "image" and "localhost" not in resp.url:
            external_images.append(resp.url)

    page.on("response", on_response)
    page.goto(f"{BASE}/index.html", wait_until="networkidle")

    # Trigger reveal animations + lazy images by scrolling through the page
    page.evaluate(
        """async () => {
            const step = window.innerHeight * 0.8;
            for (let y = 0; y < document.body.scrollHeight; y += step) {
                window.scrollTo(0, y);
                await new Promise(r => setTimeout(r, 150));
            }
            window.scrollTo(0, 0);
        }"""
    )
    page.wait_for_timeout(800)

    # Every img must actually render pixels
    broken = page.evaluate(
        """() => Array.from(document.querySelectorAll('img'))
            .filter(i => i.getAttribute('src') && i.complete && i.naturalWidth === 0)
            .map(i => i.getAttribute('src'))"""
    )

    for item in bad_requests:
        failures.append(f"[{label}] bad request: {item}")
    for item in external_images:
        failures.append(f"[{label}] external image: {item}")
    for item in broken:
        failures.append(f"[{label}] broken img: {item}")

    for section, name in [
        (".hero", "hero"),
        ("#services", "services"),
        ("#gallery", "gallery"),
        ("#about", "about"),
    ]:
        page.locator(section).screenshot(path=f"{OUT}/{label}_{name}.png")

    # Lightbox: open tile 1, step through all photos
    page.locator(".gallery-item").first.click()
    page.wait_for_selector("#lightbox:not([hidden])")
    counter = page.locator("#lightboxCounter").inner_text()
    if counter.strip() != "1 / 3":
        failures.append(f"[{label}] lightbox counter expected '1 / 3', got '{counter}'")
    page.locator("#lightboxNext").click()
    page.wait_for_timeout(300)
    page.locator("#lightboxNext").click()
    page.wait_for_timeout(300)
    lb_src = page.locator("#lightboxImg").get_attribute("src")
    if "result-01/03.jpg" not in lb_src:
        failures.append(f"[{label}] lightbox did not reach result-01/03.jpg, src={lb_src}")
    page.screenshot(path=f"{OUT}/{label}_lightbox.png")
    page.keyboard.press("Escape")


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        check_page(browser.new_page(viewport={"width": 1440, "height": 900}), "desktop")
        check_page(browser.new_page(viewport={"width": 390, "height": 844}), "mobile")
        browser.close()

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        raise SystemExit(1)
    print("PASS: all images local, all render, lightbox steps correctly (desktop + mobile)")


if __name__ == "__main__":
    main()
