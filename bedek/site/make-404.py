# -*- coding: utf-8 -*-
"""
Generates public/404.html from the palette.

Why a static file and not a React route: this page has to render when the
bundle is missing, the CDN is confused, or JS failed -- which is exactly the
class of situation that produces a 404 in the first place. It carries no
script and no imports beyond the webfont.

Called by sync-brand.py; not meant to be run alone.
"""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
C = next(
    d for d in json.load(io.open(
        os.path.join(ROOT, "brand", "palette", "directions.json"), encoding="utf-8"))
    if d["name"] == "bridge"
)["colors"]
MARK = io.open(os.path.join(ROOT, "assets", "logos", "mark.svg"), encoding="utf-8").read()

HTML = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>הדף לא נמצא · TACT בדק</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500&family=Rubik:wght@800&family=Space+Grotesk:wght@500&display=swap">
<style>
  *,*::before,*::after {{ box-sizing: border-box; }}
  body {{
    margin: 0; min-height: 100vh; background: {C['canvas']}; color: {C['inkStrong']};
    font-family: Heebo, "Segoe UI", system-ui, sans-serif; line-height: 1.6;
    display: grid; place-items: center; padding: 24px;
  }}
  main {{ display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center; }}
  svg {{ width: 64px; height: 64px; }}
  .code {{
    font-family: "Space Grotesk", monospace; font-size: 13px; letter-spacing: .18em;
    color: {C['accentDeep']}; background: {C['accentSoft']};
    border-radius: 5px; padding: 4px 11px;
  }}
  h1 {{
    margin: 0; font-family: Rubik, Heebo, sans-serif; font-weight: 800;
    font-size: clamp(26px, 5vw, 38px); letter-spacing: -.022em; line-height: 1.15;
  }}
  p {{ margin: 0; max-width: 46ch; color: {C['inkSoft']}; }}
  a {{
    margin-top: 8px; display: inline-block; background: {C['accent']}; color: #fff;
    font-weight: 700; font-size: 14px; text-decoration: none;
    border-radius: 10px; padding: 12px 22px;
  }}
  a:hover {{ background: {C['accentDeep']}; }}
  a:focus-visible {{ outline: 2px solid {C['brand']}; outline-offset: 2px; }}
</style>
</head>
<body>
  <main>
    {MARK}
    <span class="code">404</span>
    <h1>הדף הזה לא קיים</h1>
    <p>יכול להיות שהקישור ישן, או שנפלה טעות בכתובת.</p>
    <a href="/">חזרה לעמוד הבית</a>
  </main>
</body>
</html>
"""

if __name__ == "__main__":
    out = os.path.join(HERE, "public", "404.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, "w", encoding="utf-8").write(HTML)
    print("   public/404.html")
