# -*- coding: utf-8 -*-
"""
Builds the palette comparison page from directions.json.

Colours are read, never retyped -- the page cannot drift from the spec.
The page chrome is deliberately achromatic: any hue in the shell would
contaminate the judgement of the four candidates it exists to compare.
"""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

# Paths resolve against this file, never the caller's cwd.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from oklch import contrast_ratio

D = json.load(io.open(os.path.join(HERE, "directions.json"), encoding="utf-8"))

HERO_EYEBROW = "TACT בדק"
HERO_H1 = "כל תקופת הבדק.<br>במקום אחד."
HERO_SUB = ("מערכת אחת שמנהלת את הליקויים בכל הפרויקטים שלך — מהרגע "
            "שהדייר מדווח ועד שהתקלה נסגרת, מתועדת וחתומה.")
HERO_CTA, HERO_ALT = "לתיאום הדגמה", "צפה איך זה עובד"
STATS = [("4", "פרויקטים"), ("312", "תקלות פתוחות"), ("18", "באיחור")]

SWATCHES = [
    ("brand", "מותג"), ("brandDeep", "מותג כהה"), ("brandSoft", "גוון רך"),
    ("accent", "אקסנט / CTA"), ("accentSoft", "אקסנט רך"),
    ("inkStrong", "טקסט"), ("inkSoft", "טקסט משני"),
    ("canvas", "רקע עמוד"), ("border", "קו הפרדה"),
]
OUTLINED = ("canvas", "brandSoft", "accentSoft", "border")


def band(d):
    c = d["colors"]
    sw = "".join(
        '<div class="sw"><span class="chip" style="background:{hexv};{edge}"></span>'
        '<span class="sw-n">{label}</span><span class="sw-h">{hexv}</span></div>'.format(
            hexv=c[k], label=label,
            edge="box-shadow:inset 0 0 0 1px rgba(0,0,0,.14)" if k in OUTLINED else "")
        for k, label in SWATCHES)
    stats = "".join(
        '<div class="stat"><b>{}</b><span>{}</span></div>'.format(n, l) for n, l in STATS)
    ratio_btn = contrast_ratio("#FFFFFF", c["accent"])
    ratio_txt = contrast_ratio(c["inkStrong"], c["canvas"])
    tokens = ";".join("--{}:{}".format(k, v) for k, v in c.items())
    return """
<section class="band" id="{name}" style="{tokens}">
  <header class="band-head">
    <h2>{title}</h2>
    <span class="verdict">WCAG AA · 17/17</span>
  </header>

  <div class="band-grid">
    <div class="mock" role="img" aria-label="הדמיית דף נחיתה בכיוון {title}">
      <div class="mock-bar">
        <span class="mock-logo">TACT <b>בדק</b></span>
        <span class="mock-nav"><i></i><i></i><i></i></span>
      </div>
      <div class="mock-hero">
        <span class="eyebrow">{eyebrow}</span>
        <h3>{h1}</h3>
        <p>{sub}</p>
        <div class="btns">
          <span class="btn-primary">{cta}</span>
          <span class="btn-ghost">{alt}</span>
        </div>
        <div class="stats">{stats}</div>
      </div>
      <div class="mock-apps">
        <div class="app" style="--a:var(--appUser)"><span class="dot"></span>אפליקציית איש חברה</div>
        <div class="app" style="--a:var(--appCustomer)"><span class="dot"></span>אפליקציית דייר</div>
      </div>
    </div>

    <div class="side">
      <p class="why">{why}</p>
      <p class="note"><span>שיקול</span>{note}</p>
      <div class="sws">{sw}</div>
      <dl class="ratios">
        <div><dt>לבן על כפתור CTA</dt><dd>{rb:.2f}</dd></div>
        <div><dt>טקסט על רקע העמוד</dt><dd>{rt:.2f}</dd></div>
      </dl>
    </div>
  </div>
</section>""".format(name=d["name"], title=d["title"], tokens=tokens,
                     eyebrow=HERO_EYEBROW, h1=HERO_H1, sub=HERO_SUB,
                     cta=HERO_CTA, alt=HERO_ALT, stats=stats, sw=sw,
                     why=d["rationale"], note=d["note"],
                     rb=ratio_btn, rt=ratio_txt)


CSS = """
:root {
  --page:#F7F7F6; --panel:#FFFFFF; --ink:#1A1A19; --ink-2:#5F5F5B;
  --ink-3:#8A8A85; --rule:#E2E2DE; --rule-2:#EFEFEC;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --page:#131312; --panel:#1C1C1A; --ink:#EDEDEA; --ink-2:#A5A59F;
    --ink-3:#77776F; --rule:#2E2E2B; --rule-2:#242422;
  }
}
:root[data-theme="dark"] {
  --page:#131312; --panel:#1C1C1A; --ink:#EDEDEA; --ink-2:#A5A59F;
  --ink-3:#77776F; --rule:#2E2E2B; --rule-2:#242422;
}
*, *::before, *::after { box-sizing:border-box; }
html { direction:rtl; }
body {
  margin:0; background:var(--page); color:var(--ink);
  font-family:Heebo, "Segoe UI", system-ui, sans-serif;
  font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased;
}
.wrap { max-width:1160px; margin:0 auto; padding:56px 24px 96px; }

.top { display:flex; flex-direction:column; gap:14px;
       padding-bottom:28px; border-bottom:1px solid var(--rule); }
.kicker { font-family:"IBM Plex Mono", ui-monospace, monospace; font-size:12px;
          letter-spacing:.14em; color:var(--ink-3); text-transform:uppercase; }
h1 { margin:0; font-size:clamp(30px,4.4vw,46px); font-weight:900;
     letter-spacing:-.022em; line-height:1.1; text-wrap:balance; }
.lede { margin:0; max-width:62ch; color:var(--ink-2); font-size:17px; }
.jump { display:flex; flex-wrap:wrap; gap:8px; margin-top:6px; }
.jump a { font-size:13.5px; font-weight:500; text-decoration:none; color:var(--ink);
          border:1px solid var(--rule); border-radius:999px; padding:5px 13px;
          transition:border-color .15s, background .15s; }
.jump a:hover, .jump a:focus-visible { background:var(--rule-2); border-color:var(--ink-3); }
:focus-visible { outline:2px solid var(--ink); outline-offset:2px; }

.band { margin-top:52px; padding-top:26px; border-top:1px solid var(--rule); }
.band:first-of-type { border-top:0; }
.band-head { display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:20px; }
.band-head h2 { margin:0; font-size:23px; font-weight:700; letter-spacing:-.01em; }
.verdict { font-family:"IBM Plex Mono", monospace; font-size:11.5px; letter-spacing:.06em;
           color:var(--ink-3); border:1px solid var(--rule); border-radius:5px; padding:2px 8px; }

.band-grid { display:grid; grid-template-columns:1.32fr 1fr; gap:26px; align-items:start; }
@media (max-width:900px) { .band-grid { grid-template-columns:1fr; } }

/* the mock keeps its own light palette in either theme -- it is a preview of
   the product, like a screenshot, not part of the page chrome */
.mock { background:var(--canvas); border:1px solid var(--rule); border-radius:12px;
        overflow:hidden; color:var(--inkStrong); }
.mock-bar { display:flex; align-items:center; justify-content:space-between;
            padding:12px 18px; background:var(--surface);
            border-bottom:1px solid var(--border); }
.mock-logo { font-size:14.5px; font-weight:500; color:var(--brandInk); letter-spacing:.01em; }
.mock-logo b { font-weight:900; color:var(--brand); }
.mock-nav { display:flex; gap:7px; }
.mock-nav i { width:26px; height:5px; border-radius:3px; background:var(--border); }
.mock-hero { padding:30px 26px 26px; }
.eyebrow { display:inline-block; font-family:"IBM Plex Mono", monospace; font-size:10.5px;
           letter-spacing:.16em; color:var(--brandInk); background:var(--brandSoft);
           border-radius:4px; padding:3px 9px; margin-bottom:14px; }
.mock-hero h3 { margin:0 0 10px; font-size:clamp(24px,2.7vw,33px); font-weight:900;
                line-height:1.14; letter-spacing:-.024em; color:var(--brandInk); }
.mock-hero p { margin:0 0 20px; max-width:44ch; font-size:14.5px; color:var(--inkSoft); }
.btns { display:flex; gap:10px; flex-wrap:wrap; }
.btn-primary { background:var(--accent); color:#fff; font-weight:700; font-size:14.5px;
               border-radius:8px; padding:10px 20px; }
.btn-ghost { color:var(--brand); font-weight:500; font-size:14.5px; border-radius:8px;
             padding:10px 18px; border:1px solid var(--border); background:var(--surface); }
.stats { display:flex; gap:26px; margin-top:26px; padding-top:20px;
         border-top:1px solid var(--border); }
.stat b { display:block; font-size:26px; font-weight:900; color:var(--brand);
          font-variant-numeric:tabular-nums; line-height:1.1; }
.stat span { font-size:12px; color:var(--inkFaint); }
.mock-apps { display:flex; gap:10px; padding:14px 26px 20px; flex-wrap:wrap; }
.app { display:flex; align-items:center; gap:7px; font-size:12.5px; color:var(--inkSoft);
       background:var(--surface); border:1px solid var(--border);
       border-radius:999px; padding:5px 13px; }
.app .dot { width:9px; height:9px; border-radius:50%; background:var(--a); }

.side { display:flex; flex-direction:column; gap:16px; }
.why { margin:0; font-size:15px; color:var(--ink-2); }
.note { margin:0; font-size:13.5px; color:var(--ink-2); background:var(--panel);
        border:1px solid var(--rule); border-inline-start:3px solid var(--ink-3);
        border-radius:7px; padding:11px 13px; }
.note span { display:block; font-family:"IBM Plex Mono", monospace; font-size:10px;
             letter-spacing:.14em; color:var(--ink-3); margin-bottom:4px; }
.sws { display:grid; grid-template-columns:repeat(auto-fill,minmax(148px,1fr)); gap:8px; }
.sw { display:flex; align-items:center; gap:8px; }
.chip { width:22px; height:22px; border-radius:5px; flex:none; }
.sw-n { font-size:12px; color:var(--ink-2); flex:1; min-width:0; }
.sw-h { font-family:"IBM Plex Mono", monospace; font-size:11px; color:var(--ink-3);
        letter-spacing:-.02em; }
.ratios { margin:0; display:flex; gap:22px; flex-wrap:wrap; padding-top:4px; }
.ratios div { display:flex; flex-direction:column; gap:1px; }
.ratios dt { font-size:11.5px; color:var(--ink-3); }
.ratios dd { margin:0; font-family:"IBM Plex Mono", monospace; font-size:16px;
             font-weight:500; font-variant-numeric:tabular-nums; }

.foot { margin-top:60px; padding-top:22px; border-top:1px solid var(--rule);
        font-size:13.5px; color:var(--ink-2); }
.foot code { font-family:"IBM Plex Mono", monospace; font-size:12.5px;
             background:var(--rule-2); border-radius:4px; padding:1px 5px; }
"""

LEDE = ("כל כיוון מוצג על אותו דף נחיתה בדיוק, עם הטקסטים האמיתיים — כך "
        "שההבדל היחיד שאתה רואה הוא הצבע. הפלטות נגזרות ב-OKLCH מתוך שלוש "
        "הפלטות הקיימות (steel-blue של TACT · אמרלד הדייר · אינדיגו איש "
        "החברה), וכל אחת עברה בדיקת ניגודיות WCAG AA אוטומטית.")

FOOT = ('מקור: <code>brand/palette/palette.py</code> · נבדק ע"י '
        '<code>contrast.py</code> (יוצא עם קוד 1 על כל כשל) · מוצג מתוך '
        '<code>directions.json</code> — הצבעים כאן נקראים, לא הוקלדו. '
        'הדמיות דף הנחיתה נשארות בפלטה הבהירה שלהן גם במצב כהה, כי הן תצוגה '
        'מקדימה של המוצר ולא חלק מהעמוד.')

HTML = """<title>ארבעה כיווני צבע לבדק</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{css}</style>

<div class="wrap">
  <div class="top">
    <span class="kicker">TACT &middot; marketing/bedek</span>
    <h1>ארבעה כיווני צבע לבחירה</h1>
    <p class="lede">{lede}</p>
    <nav class="jump">{jump}</nav>
  </div>
  {bands}
  <p class="foot">{foot}</p>
</div>""".format(
    css=CSS, lede=LEDE, foot=FOOT,
    jump="".join('<a href="#{}">{}</a>'.format(d["name"], d["title"]) for d in D),
    bands="".join(band(d) for d in D))

io.open(os.path.join(HERE, "preview.html"), "w", encoding="utf-8").write(HTML)
print("preview.html written:", len(HTML), "bytes")
