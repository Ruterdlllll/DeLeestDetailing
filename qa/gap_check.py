"""Diagnose the hero -> services gap on mobile: measure layout + shoot the boundary."""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080"
OUT = "qa-screenshots/gap-check"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 390, "height": 844},
                            is_mobile=True, has_touch=True,
                            device_scale_factor=2)
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_timeout(600)

    # Force-reveal everything so animations don't skew the measurement
    page.evaluate("document.querySelectorAll('.reveal').forEach(e => e.classList.add('visible'))")

    metrics = page.evaluate("""() => {
      const hero = document.querySelector('.hero');
      const services = document.querySelector('#services');
      const kicker = services.querySelector('.kicker');
      return {
        viewportH: window.innerHeight,
        heroH: Math.round(hero.getBoundingClientRect().height),
        heroBottom: Math.round(hero.getBoundingClientRect().bottom),
        servicesPaddingTop: getComputedStyle(services).paddingTop,
        gapPx: Math.round(kicker.getBoundingClientRect().top - hero.getBoundingClientRect().bottom),
      };
    }""")
    print("metrics:", metrics)

    # Screenshot the boundary: scroll so the hero bottom is mid-screen
    page.evaluate("window.scrollTo(0, document.querySelector('.hero').offsetHeight - 300)")
    page.wait_for_timeout(800)
    page.screenshot(path=f"{OUT}-boundary.png")

    # And right at services start
    page.evaluate("window.scrollTo(0, document.querySelector('#services').offsetTop - 200)")
    page.wait_for_timeout(800)
    page.screenshot(path=f"{OUT}-services.png")

    browser.close()
print("done")
