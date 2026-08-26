# -*- coding: utf-8 -*-
"""
Profile picture and cover image for the Facebook Page.

Rendered in Chromium from the brand tokens rather than drawn by hand, so a
palette change re-generates them. The mark comes from assets/logos.

    python assets.py   -> social/out/profile.png  +  social/out/cover.png

Sizes and the reason for each:
  profile 1080x1080  Displayed as a circle at ~176px on desktop and ~128px on
                     mobile. Anything near the corners is cropped away, so the
                     mark sits well inside a centred safe circle.
  cover   1640x856   Facebook crops this hard: roughly 820x312 on desktop and
                     a much narrower centre band on mobile. Everything that
                     must survive lives inside a centred safe box, which the
                     --safe outline makes visible during design.
"""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "out")

C = next(
    d for d in json.load(io.open(
        os.path.join(ROOT, "brand", "palette", "directions.json"), encoding="utf-8"))
    if d["name"] == "bridge"
)["colors"]
MARK_REV = io.open(os.path.join(ROOT, "assets", "logos", "mark-reverse.svg"),
                   encoding="utf-8").read()

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Heebo:wght@400;500&family=Rubik:wght@800&'
         'family=Space+Grotesk:wght@500&display=swap">')

SHOW_SAFE = "--safe" in sys.argv


def page(w, h, css, body):
    return f"""<!doctype html><meta charset="utf-8">{FONTS}
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{width:{w}px;height:{h}px;overflow:hidden;direction:rtl;
    font-family:Heebo,sans-serif;-webkit-font-smoothing:antialiased}}
  {css}
</style>{body}"""


PROFILE = page(1080, 1080, f"""
  body{{background:{C['brand']};display:grid;place-items:center}}
  /* the whole composition sits inside the circle Facebook crops to */
  .safe{{width:1080px;height:1080px;border-radius:50%;display:grid;
    place-items:center;
    background:radial-gradient(70% 70% at 30% 22%,
      rgba(255,255,255,.13) 0%, transparent 62%)}}
  svg{{width:620px;height:620px}}
  .ring{{position:absolute;width:1010px;height:1010px;border-radius:50%;
    border:3px solid rgba(255,255,255,.16)}}
""", f'<div class="safe"><div class="ring"></div>{MARK_REV}</div>')


COVER = page(1640, 856, f"""
  body{{background:
      radial-gradient(90% 120% at 78% -20%, rgba(255,255,255,.16) 0%, transparent 58%),
      {C['brand']};
    display:grid;place-items:center;color:#fff}}
  .safe{{width:1140px;height:430px;display:flex;align-items:center;
    justify-content:center;gap:60px;
    {'outline:2px dashed rgba(255,255,255,.5);' if SHOW_SAFE else ''}}}
  svg{{width:236px;height:236px;flex:none}}
  .txt{{display:flex;flex-direction:column;align-items:flex-start;gap:8px}}
  .grp{{font-family:"Space Grotesk",monospace;font-weight:500;font-size:27px;
    letter-spacing:.26em;direction:ltr;unicode-bidi:isolate;
    color:rgba(255,255,255,.85)}}
  .grp i{{font-style:normal;color:{C['accent']}}}
  .word{{font-family:Rubik,Heebo,sans-serif;font-weight:800;font-size:140px;
    line-height:1;letter-spacing:-.03em}}
  .tag{{font-size:31px;color:rgba(255,255,255,.88);margin-top:6px}}
""", f"""<div class="safe">{MARK_REV}<div class="txt">
  <span class="grp">T<i>·</i>A<i>·</i>C<i>·</i>T</span>
  <span class="word">בדק</span>
  <span class="tag">ניהול ליקויי בנייה בתקופת הבדק</span>
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
            path = os.path.join(OUT, f"{name}.png")
            pg.screenshot(path=path)
            pg.close()
            print(f"   {name}.png  {w}x{h}")
        b.close()
    print(f"\n-> {OUT}")
