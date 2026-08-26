# -*- coding: utf-8 -*-
"""Renders the four marks side by side to a PNG, for eyeballing the geometry."""
import io, sys, glob, os
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

files = sorted(f for f in glob.glob("marks/*.svg") if "-mono" not in f)
cells = "".join(
    '<div><div class="big">{s}</div><div class="sm">{s}</div><code>{n}</code></div>'.format(
        s=io.open(f, encoding="utf-8").read(), n=os.path.basename(f))
    for f in files)
html = """<!doctype html><meta charset="utf-8"><style>
body{margin:0;background:#fff;font-family:monospace;display:flex;gap:26px;padding:26px}
div>div{display:grid;place-items:center}
.big svg{width:120px;height:120px}.sm svg{width:22px;height:22px;margin-top:10px}
code{display:block;text-align:center;margin-top:10px;font-size:11px;color:#888}
</style>""" + cells

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 760, "height": 230})
    pg.set_content(html)
    pg.screenshot(path="marks/_contact-sheet.png")
    b.close()
print("marks/_contact-sheet.png")
