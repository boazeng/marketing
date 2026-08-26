# -*- coding: utf-8 -*-
"""
The beats that carry Hebrew type, rendered in Chromium instead of generated.

Video models cannot render readable Hebrew -- they produce letter-shaped noise.
So every frame the viewer must actually READ is drawn here, from the same
palette and fonts as the site, and only the live-action B-roll comes from fal.

Rendered as PNG sequences rather than CSS animation: @keyframes are not
deterministic under frame-by-frame capture, so the clock is advanced by hand
and each frame is drawn from a pure function of t. Same input, same film.

    python make_cards.py
"""
import io, json, math, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "cards")
sys.path.insert(0, HERE)
from scripts import VIDEOS  # noqa: E402

C = next(d for d in json.load(io.open(
    os.path.join(ROOT, "brand", "palette", "directions.json"), encoding="utf-8"))
    if d["name"] == "bridge")["colors"]
MARK = io.open(os.path.join(ROOT, "assets", "logos", "mark-reverse.svg"),
               encoding="utf-8").read()

W, H, FPS = 1280, 720, 30          # standard rate; build.py conforms the clips

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Heebo:wght@400;500&family=Rubik:wght@800&'
         'family=Space+Grotesk:wght@500&display=swap">')


def ease(t):
    """easeOutCubic -- motion that settles rather than stops."""
    return 1 - pow(1 - max(0.0, min(1.0, t)), 3)


def page(kind, text, sub=""):
    """`turn` is the pivot from pain to promise; `end` is the sign-off."""
    logo = f"""<span class="logo">{MARK}<span class="ltxt">
        <span class="grp">T<i>·</i>A<i>·</i>C<i>·</i>T</span>
        <span class="word">בדק</span></span></span>"""
    body = (f'<div class="turn"><span class="line"></span><h1>{text}</h1></div>'
            if kind == "turn" else
            f'<div class="end">{logo}<h2>{text}</h2><span class="url">{sub}</span></div>')
    return f"""<!doctype html><meta charset="utf-8">{FONTS}<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;direction:rtl;background:{C['brand']};
  font-family:Heebo,sans-serif;color:#fff;-webkit-font-smoothing:antialiased}}
body{{display:grid;place-items:center;
  background:radial-gradient(80% 110% at 74% -12%,rgba(255,255,255,.15) 0%,transparent 60%),{C['brand']}}}
.turn{{display:flex;flex-direction:column;align-items:center;gap:26px;opacity:0}}
.line{{width:0;height:4px;border-radius:2px;background:{C['accent']}}}
h1{{font-family:Rubik,Heebo,sans-serif;font-weight:800;font-size:66px;
  letter-spacing:-.03em;text-align:center;line-height:1.15}}
.end{{display:flex;flex-direction:column;align-items:center;gap:20px;opacity:0}}
.logo{{display:flex;align-items:center;gap:20px}}
.logo svg{{width:104px;height:104px}}
.ltxt{{display:flex;flex-direction:column;align-items:flex-start;gap:4px}}
.grp{{font-family:"Space Grotesk",monospace;font-weight:500;font-size:19px;
  letter-spacing:.26em;direction:ltr;unicode-bidi:isolate;color:rgba(255,255,255,.85)}}
.grp i{{font-style:normal;color:{C['accent']}}}
.word{{font-family:Rubik,Heebo,sans-serif;font-weight:800;font-size:76px;line-height:1;
  letter-spacing:-.03em}}
h2{{font-family:Rubik,Heebo,sans-serif;font-weight:800;font-size:40px;
  letter-spacing:-.02em;margin-top:8px}}
.url{{font-family:"Space Grotesk",monospace;font-size:25px;letter-spacing:.06em;
  color:{C['accent']};direction:ltr;unicode-bidi:isolate}}
</style>{body}
<script>
// Pure function of t. render.py advances the clock; nothing animates itself.
window.SEEK = function (t, dur) {{
  var e = function (x) {{ x = Math.max(0, Math.min(1, x)); return 1 - Math.pow(1 - x, 3); }};
  var inn = e(t / 0.55);
  var out = t > dur - 0.35 ? e((dur - t) / 0.35) : 1;
  var turn = document.querySelector('.turn'), end = document.querySelector('.end');
  var el = turn || end;
  el.style.opacity = String(inn * out);
  el.style.transform = 'translateY(' + ((1 - inn) * 18).toFixed(2) + 'px)';
  var line = document.querySelector('.line');
  if (line) line.style.width = (e((t - 0.25) / 0.7) * 190).toFixed(1) + 'px';
}};
</script>"""


CARDS = {
    "sheket": {
        "a3": ("turn", "בדק עושה את זה אחרת.", ""),
        "a7": ("end", "השקט חוזר אליך", "yazam-il.com"),
    },
    "shlita": {
        "b3": ("turn", "אם אתה צריך לחפש\nאין לך שליטה", ""),
        "b7": ("end", "הכל מתועד", "yazam-il.com"),
    },
}


def render(slug, bid, kind, text, sub, seconds):
    from playwright.sync_api import sync_playwright
    frames = int(round(seconds * FPS))
    d = os.path.join(OUT, f"{slug}-{bid}")
    os.makedirs(d, exist_ok=True)
    html = page(kind, text.replace("\n", "<br>"), sub)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.set_content(html)
        pg.wait_for_timeout(2200)              # webfonts
        for i in range(frames):
            pg.evaluate("([t,d]) => window.SEEK(t,d)", [i / FPS, seconds])
            pg.screenshot(path=os.path.join(d, f"{i:04d}.png"))
        b.close()
    mp4 = os.path.join(HERE, "clips", f"{slug}-{bid}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(d, "%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", mp4],
                   check=True)
    print(f"  {slug}-{bid}  {seconds:.2f}s  {frames} frames")


if __name__ == "__main__":
    timing = json.load(io.open(os.path.join(HERE, "audio", "timing.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    for v in VIDEOS:
        secs = {b["id"]: b["sec"] for b in timing[v["slug"]]["beats"]}
        for bid, (kind, text, sub) in CARDS[v["slug"]].items():
            # +0.5s so the card holds a beat after the line lands
            render(v["slug"], bid, kind, text, sub, secs[bid] + 0.5)
