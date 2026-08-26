# -*- coding: utf-8 -*-
"""Full-page screenshots of both pages, desktop and phone."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

SHOTS = [("index", "http://localhost:5340/", 1440, 900),
         ("index-mobile", "http://localhost:5340/", 390, 844),
         ("landing", "http://localhost:5340/landing.html", 1440, 900)]

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, url, w, h in SHOTS:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(url, wait_until="networkidle")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=f"_shot-{name}.png", full_page=True)
        wide = pg.evaluate(
            "document.documentElement.scrollWidth > document.documentElement.clientWidth")
        print(f"{name:14} h={pg.evaluate('document.body.scrollHeight'):5}  "
              f"horizontal-overflow={wide}")
        pg.close()
    b.close()
