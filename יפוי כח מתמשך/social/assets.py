# -*- coding: utf-8 -*-
"""
Profile picture and cover image for the Facebook Page.

Rendered in Chromium, same as bedek/social/assets.py -- see there for why the
sizes and safe areas are what they are.

    python assets.py          -> social/out/profile.png  +  social/out/cover.png
    python assets.py --safe   outline the area that survives Facebook's crop

There is no brand/palette for this project yet. The colours and the scales
mark are lifted from the landing page in SharePoint (TACT/שיווק/יפוי כח מתמשך/אתר)
so the Page and the page it links to look like one thing. When a palette is
compiled, read it from there instead of the constants below.
"""
import os, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

NAVY_DEEP, NAVY, GOLD, GOLD_SOFT = "#0a1a2e", "#0f2744", "#c4a35a", "#e8d5a3"

# Every word on the cover is public advertising by a lawyer: it states who and
# what, and nothing that reads as a promise or a comparison. See DECISIONS.md.
NAME = "עו״ד זהר אנגלנדר"
SERVICE = "ייפוי כוח מתמשך"

MARK = """<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M32 8v40M20 48h24M14 54h36M12 22h40" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
  <circle cx="32" cy="14" r="3.2" fill="currentColor"/>
  <path d="M18 22l-8 14c0 4.4 3.6 8 8 8s8-3.6 8-8l-8-14z" stroke="currentColor" stroke-width="2" fill="currentColor" fill-opacity="0.18"/>
  <path d="M46 22l-8 14c0 4.4 3.6 8 8 8s8-3.6 8-8l-8-14z" stroke="currentColor" stroke-width="2" fill="currentColor" fill-opacity="0.18"/>
</svg>"""

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Heebo:wght@400;500;800&display=swap">')

SHOW_SAFE = "--safe" in sys.argv
BG = (f"radial-gradient(ellipse 80% 60% at 100% 0%, rgba(196,163,90,.22), transparent 55%),"
      f"linear-gradient(145deg, {NAVY_DEEP} 0%, {NAVY} 55%, #163a5f 100%)")


def page(w, h, css, body):
    return f"""<!doctype html><meta charset="utf-8">{FONTS}
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{width:{w}px;height:{h}px;overflow:hidden;direction:rtl;
    font-family:Heebo,sans-serif;-webkit-font-smoothing:antialiased}}
  {css}
</style>{body}"""


PROFILE = page(1080, 1080, f"""
  body{{background:{BG};display:grid;place-items:center;color:{GOLD_SOFT}}}
  svg{{width:600px;height:600px}}
  .ring{{position:absolute;width:1010px;height:1010px;border-radius:50%;
    border:3px solid rgba(232,213,163,.22)}}
""", f'<div class="ring"></div>{MARK}')


COVER = page(1640, 856, f"""
  body{{background:{BG};display:grid;place-items:center;color:#fff}}
  .safe{{width:1140px;height:430px;display:flex;align-items:center;
    justify-content:center;gap:64px;
    {'outline:2px dashed rgba(255,255,255,.5);' if SHOW_SAFE else ''}}}
  svg{{width:230px;height:230px;flex:none;color:{GOLD_SOFT}}}
  .txt{{display:flex;flex-direction:column;align-items:flex-start;gap:10px}}
  .name{{font-size:40px;font-weight:500;color:{GOLD_SOFT}}}
  .word{{font-weight:800;font-size:104px;line-height:1.1;letter-spacing:-.02em}}
""", f"""<div class="safe">{MARK}<div class="txt">
  <span class="name">{NAME}</span>
  <span class="word">{SERVICE}</span>
</div></div>""")


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    os.makedirs(OUT, exist_ok=True)
    jobs = [("profile", PROFILE, 1080, 1080), ("cover", COVER, 1640, 856)]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, html, w, h in jobs:
            pg = b.new_page(viewport={"width": w, "height": h},
                            device_scale_factor=1)
            pg.set_content(html)
            pg.wait_for_timeout(2000)      # webfonts must land before capture
            pg.screenshot(path=os.path.join(OUT, f"{name}.png"))
            pg.close()
            print(f"   {name}.png  {w}x{h}")
        b.close()
    print(f"\n-> {OUT}")
