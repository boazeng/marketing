# -*- coding: utf-8 -*-
"""
Five logo directions for TACT Bedek, plus the display-face candidates.

Marks are generated, not drawn by hand, so the palette is the single source
of truth for colour and every direction sits on the same 64x64 grid -- which
is what makes them honestly comparable.

    python logos.py    -> marks/*.svg  +  logos.html
"""
import io, json, math, sys

sys.stdout.reconfigure(encoding="utf-8")

PAL = json.load(io.open("../palette/directions.json", encoding="utf-8"))
C = next(d for d in PAL if d["name"] == "bridge")["colors"]

VB = 64  # every mark lives on the same 64x64 grid


# ---------------------------------------------------------------- the marks
def m_address(brand, accent):
    """A 3x3 of units; one carries the accent. Every defect has an address --
    building, entrance, floor, unit -- which is the product's core idea. Also
    inherits TACT's dot device without borrowing its colour."""
    cell, gap, off = 15.0, 5.5, 4.0
    out = []
    for r in range(3):
        for c in range(3):
            x, y = off + c * (cell + gap), off + r * (cell + gap)
            if (r, c) == (1, 1):
                out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                           f'rx="3.6" fill="{accent}"/>')
            else:
                out.append(f'<rect x="{x + 1.3}" y="{y + 1.3}" width="{cell - 2.6}" '
                           f'height="{cell - 2.6}" rx="2.6" fill="none" '
                           f'stroke="{brand}" stroke-width="2.6"/>')
    return "".join(out)


def m_bet(brand, accent):
    """The letter bet -- of BEDEK, and the shape of a house -- with the accent
    sitting inside it. Unreadable to a non-Hebrew eye, which here costs
    nothing: the audience is entirely Israeli."""
    return (f'<g fill="none" stroke="{brand}" stroke-width="7.5" '
            f'stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M18 15 H44 V49"/><path d="M52 49 H12"/></g>'
            f'<circle cx="30" cy="31" r="5.4" fill="{accent}"/>')


def m_loop(brand, accent):
    """The defect lifecycle closing: reported, assigned, fixed, signed. The
    accent is the dot that shuts the ring."""
    cx = cy = 32.0
    r, dot = 21.0, 6.0
    # Two things keep this from reading as a power button. The arc caps stop
    # exactly where the dot begins -- zero clearance, no daylight. And the
    # break sits at 305 degrees, not at twelve o'clock: a power glyph is
    # always symmetrical about the vertical axis, so breaking that symmetry
    # kills the association outright. 305 is also where an RTL eye starts.
    brk = 305.0
    half = math.degrees(math.atan(dot / r)) + math.degrees(math.atan(3.75 / r))
    a0, a1 = math.radians(brk + half), math.radians(brk - half)
    p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
    p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    pg = (cx + r * math.cos(math.radians(brk)), cy + r * math.sin(math.radians(brk)))
    return (f'<path d="M{p0[0]:.2f} {p0[1]:.2f} A{r} {r} 0 1 1 {p1[0]:.2f} {p1[1]:.2f}" '
            f'fill="none" stroke="{brand}" stroke-width="7" stroke-linecap="round"/>'
            f'<circle cx="{pg[0]:.2f}" cy="{pg[1]:.2f}" r="{dot}" fill="{accent}"/>')


def m_floors(brand, accent):
    """Three volumes on one baseline -- a skyline -- with the middle one
    carrying the accent: the project that needs attention.

    Two earlier cuts were thrown out here. Free-floating bars read as a
    text-align icon; an outlined box with courses inside read as a document.
    A filled massing is the version that actually says 'building'."""
    base, w, gap = 53.0, 11.5, 3.5
    tops = [30.0, 16.0, 35.0]
    x0 = 32 - (3 * w + 2 * gap) / 2
    return "".join(
        f'<rect x="{x0 + i * (w + gap):.1f}" y="{t}" width="{w}" '
        f'height="{base - t}" rx="2.6" fill="{accent if i == 1 else brand}"/>'
        for i, t in enumerate(tops))


MARKS = [
    ("address", "א׳ · כתובת", m_address,
     "רשת של תשע יחידות, אחת מהן נושאת את האקסנט. זה בדיוק המוצר: לכל תקלה יש "
     "כתובת מדויקת — בניין, כניסה, קומה, יחידת ממכר. הנקודה היא גם המכשיר "
     "הגרפי של TACT (‏T∙A∙C∙T), בלי לשאול את צבע הראסט.",
     "הכי קרוב למותג האם והכי \"מערכת\". החיסרון: רשתות של ריבועים הן שפה נפוצה בתוכנה."),
    ("bet", "ב׳ · האות ב", m_bet,
     "האות ב׳ — של בדק, וגם צורת בית — עם האקסנט יושב בתוכה. הצורה הכי "
     "ישראלית מבין החמש, ומיד מזוהה עם השם.",
     "לא נקראת לעין לא-עברית. כאן זה לא מחיר — הקהל ישראלי לחלוטין. "
     "לשים לב: ב׳ צרה מדי בפאביקון קטן."),
    ("loop", "ג׳ · מעגל נסגר", m_loop,
     "מחזור החיים של התקלה: מדווחת, משויכת, מטופלת, חתומה. הנקודה בענבר היא "
     "מה שסוגר את הטבעת — כלומר ההבטחה של המוצר בתמונה אחת.",
     "האמירה הכי חזקה מבין החמש. גם הצורה הגנרית ביותר — טבעת עם פתח היא "
     "לוגו של הרבה מוצרי SaaS."),
    ("floors", "ד׳ · קומות", m_floors,
     "חזית בניין בארבע שורות; השורה הקצרה בענבר היא הקומה שדורשת טיפול. "
     "אומרת \"בנייה\" בלי לצייר מנוף או קסדה.",
     "הכי קריאה בגודל קטן ובמונוכרום. הכי פחות \"טכנולוגית\"."),
]

FACES = [
    ("Rubik", 800, "רוביק",
     "גיאומטרי עם פינות מעוגלות קלות. טווח משקלים מלא, כך שאותה משפחה עובדת "
     "בכותרת ובתווית. הכי בטוח מבין השלושה."),
    ("Suez One", 400, "סואץ וואן",
     "דיספליי כבד עם נגיעה סלאבית — יש לו כובד ש\"בנייה\" צריכה. משקל אחד "
     "בלבד, ולכן לכותרות בלבד."),
    ("Secular One", 400, "סקולר וואן",
     "שחור וצפוף, קונטרסט גבוה מול גוף טקסט קל. משקל אחד. אגרסיבי — "
     "עובד בכותרת ענקית, נשבר בכותרת בינונית."),
]


def svg(inner, size=None, bg=None):
    dim = f' width="{size}" height="{size}"' if size else ""
    ground = (f'<rect width="{VB}" height="{VB}" rx="14" fill="{bg}"/>') if bg else ""
    return (f'<svg viewBox="0 0 {VB} {VB}"{dim} xmlns="http://www.w3.org/2000/svg" '
            f'role="img">{ground}{inner}</svg>')


def wordmark(face, weight, brand, accent, scale=1.0):
    """TACT locked LTR above the product name, the dot device in accent."""
    return f"""
<span class="wm" style="--s:{scale}">
  <span class="wm-tact" style="color:{brand}">T<i style="color:{accent}">.</i>A<i style="color:{accent}">.</i>C<i style="color:{accent}">.</i>T</span>
  <span class="wm-word" style="font-family:'{face}',Heebo,sans-serif;font-weight:{weight};color:{brand}">בדק</span>
</span>"""


# ---------------------------------------------------------------- the board
def direction_block(key, title, fn, why, note):
    brand, accent, ink = C["brand"], C["accent"], C["inkStrong"]
    return f"""
<section class="dir" id="{key}">
  <header class="dir-head"><h2>{title}</h2><code>{key}</code></header>
  <div class="dir-grid">
    <div class="stage">
      <div class="lockup">
        <span class="mark-lg">{svg(fn(brand, accent))}</span>
        {wordmark('Rubik', 800, brand, accent)}
      </div>
    </div>
    <div class="side">
      <p class="why">{why}</p>
      <p class="note"><span>שיקול</span>{note}</p>
      <div class="tests">
        <figure><span class="t t-plain">{svg(fn(brand, accent), 40)}</span><figcaption>40px</figcaption></figure>
        <figure><span class="t t-plain">{svg(fn(brand, accent), 18)}</span><figcaption>פאביקון 18px</figcaption></figure>
        <figure><span class="t">{svg(fn('#FFFFFF', C['accentSoft']), 40, brand)}</span><figcaption>היפוך</figcaption></figure>
        <figure><span class="t t-plain">{svg(fn(ink, ink), 40)}</span><figcaption>מונוכרום</figcaption></figure>
      </div>
    </div>
  </div>
</section>"""


def face_block():
    rows = "".join(f"""
  <div class="face">
    <div class="face-spec" style="font-family:'{f}',Heebo,sans-serif;font-weight:{w};color:{C['brand']}">כל תקופת הבדק</div>
    <div class="face-meta"><b>{f}</b> <span>{he}</span></div>
    <p>{d}</p>
  </div>""" for f, w, he, d in FACES)
    return f"""
<section class="dir" id="type">
  <header class="dir-head"><h2>פונט הכותרות</h2><code>display</code></header>
  <p class="why" style="margin:0 0 20px">גוף הטקסט והממשק נשארים <b>Heebo</b> — אותו
    פונט כמו ב-TACT ובשתי האפליקציות. מספרים ואנגלית ב-<b>Space Grotesk</b>, גם זו
    כבר מוסכמה של TACT. מה שנותר להחליט הוא פונט הכותרות, שהוא גם הפונט של
    הוורדמארק. שלושת המועמדים זמינים ב-Google Fonts — כלומר נטענים באתר בלי רישוי.</p>
  <div class="faces">{rows}</div>
</section>"""


CSS = """
:root { --page:#F7F7F6; --panel:#FFFFFF; --ink:#1A1A19; --ink-2:#5F5F5B;
        --ink-3:#8A8A85; --rule:#E2E2DE; --rule-2:#EFEFEC; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --page:#131312; --panel:#1C1C1A; --ink:#EDEDEA; --ink-2:#A5A59F;
    --ink-3:#77776F; --rule:#2E2E2B; --rule-2:#242422; } }
:root[data-theme="dark"] {
  --page:#131312; --panel:#1C1C1A; --ink:#EDEDEA; --ink-2:#A5A59F;
  --ink-3:#77776F; --rule:#2E2E2B; --rule-2:#242422; }
*, *::before, *::after { box-sizing:border-box; }
html { direction:rtl; }
body { margin:0; background:var(--page); color:var(--ink);
       font-family:Heebo,"Segoe UI",system-ui,sans-serif; font-size:16px;
       line-height:1.6; -webkit-font-smoothing:antialiased; }
.wrap { max-width:1120px; margin:0 auto; padding:56px 24px 96px; }
.top { display:flex; flex-direction:column; gap:14px; padding-bottom:26px;
       border-bottom:1px solid var(--rule); }
.kicker { font-family:"Space Grotesk",ui-monospace,monospace; font-size:12px;
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

.dir { margin-top:48px; padding-top:26px; border-top:1px solid var(--rule); }
.dir-head { display:flex; align-items:baseline; gap:12px; margin-bottom:20px; }
.dir-head h2 { margin:0; font-size:22px; font-weight:700; letter-spacing:-.01em; }
.dir-head code { font-family:"Space Grotesk",monospace; font-size:11.5px;
                 color:var(--ink-3); border:1px solid var(--rule);
                 border-radius:5px; padding:2px 8px; }
.dir-grid { display:grid; grid-template-columns:1fr 1fr; gap:24px; align-items:start; }
@media (max-width:880px) { .dir-grid { grid-template-columns:1fr; } }

/* the stage stays in the brand's own light ground in either theme -- a logo
   is judged against the surface it will actually sit on */
.stage { background:#FFFFFF; border:1px solid var(--rule); border-radius:12px;
         min-height:190px; display:grid; place-items:center; padding:30px 20px; }
.lockup { display:flex; align-items:center; gap:18px; }
.mark-lg svg { width:66px; height:66px; display:block; }
.wm { display:flex; flex-direction:column; align-items:flex-start; gap:2px; }
.wm-tact { font-family:"Space Grotesk",monospace; font-weight:500;
           font-size:calc(13px * var(--s,1)); letter-spacing:.24em;
           direction:ltr; unicode-bidi:isolate; }
.wm-tact i { font-style:normal; }
.wm-word { font-size:calc(42px * var(--s,1)); line-height:1;
           letter-spacing:-.02em; }

.side { display:flex; flex-direction:column; gap:15px; }
.why { margin:0; font-size:15px; color:var(--ink-2); }
.note { margin:0; font-size:13.5px; color:var(--ink-2); background:var(--panel);
        border:1px solid var(--rule); border-inline-start:3px solid var(--ink-3);
        border-radius:7px; padding:11px 13px; }
.note span { display:block; font-family:"Space Grotesk",monospace; font-size:10px;
             letter-spacing:.14em; color:var(--ink-3); margin-bottom:4px; }
.tests { display:flex; gap:14px; flex-wrap:wrap; }
.tests figure { margin:0; display:flex; flex-direction:column; align-items:center; gap:6px; }
.t { display:grid; place-items:center; width:62px; height:62px; border-radius:10px;
     border:1px solid var(--rule); overflow:hidden; }
.t-plain { background:#FFFFFF; }
.tests figcaption { font-size:11px; color:var(--ink-3); }

.faces { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }
.face { background:#FFFFFF; border:1px solid var(--rule); border-radius:12px; padding:20px; }
.face-spec { font-size:31px; line-height:1.15; letter-spacing:-.02em; margin-bottom:12px; }
.face-meta { font-size:13px; color:#5F5F5B; margin-bottom:6px; }
.face-meta b { font-family:"Space Grotesk",monospace; font-weight:500; }
.face-meta span { color:#8A8A85; }
.face p { margin:0; font-size:13.5px; color:#5F5F5B; }

.foot { margin-top:56px; padding-top:22px; border-top:1px solid var(--rule);
        font-size:13.5px; color:var(--ink-2); }
.foot code { font-family:"Space Grotesk",monospace; font-size:12.5px;
             background:var(--rule-2); border-radius:4px; padding:1px 5px; }
"""

WORDMARK_ONLY = f"""
<section class="dir" id="wordmark">
  <header class="dir-head"><h2>ה׳ · וורדמארק בלבד</h2><code>wordmark</code></header>
  <div class="dir-grid">
    <div class="stage"><div class="lockup">{wordmark('Rubik', 800, C['brand'], C['accent'], 1.25)}</div></div>
    <div class="side">
      <p class="why">בלי סמל. השם עצמו הוא הסימן, והנקודות בענבר — המכשיר
        הגרפי שכבר קיים ב-‏T∙A∙C∙T — הן כל הקישוט. הכי מהיר להוציא לפועל,
        והכי קשה לעשות רע.</p>
      <p class="note"><span>שיקול</span>בלי סמל אין אייקון לאפליקציה, אין
        פאביקון ואין תמונת פרופיל לאינסטגרם. בפועל תצטרך סמל בהמשך בכל מקרה —
        השאלה היא רק אם עכשיו או אחר כך.</p>
    </div>
  </div>
</section>"""

blocks = "".join(direction_block(*m) for m in MARKS) + WORDMARK_ONLY + face_block()
jump = "".join(f'<a href="#{k}">{t}</a>' for k, t, *_ in MARKS) \
     + '<a href="#wordmark">ה׳ · וורדמארק</a><a href="#type">פונט הכותרות</a>'

HTML = f"""<title>סימן ואות לבדק</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;900&family=Rubik:wght@500;700;800&family=Secular+One&family=Suez+One&family=Space+Grotesk:wght@400;500;700&display=swap">
<style>{CSS}</style>
<div class="wrap">
  <div class="top">
    <span class="kicker">TACT &middot; marketing/bedek</span>
    <h1>חמישה כיווני סימן</h1>
    <p class="lede">כולם בפלטה שנבחרה — <b>א׳ גשר</b> — ועל אותה רשת 64&times;64,
      כדי שההשוואה תהיה הוגנת. לכל כיוון מוצגות ארבע הבדיקות שסימן חייב לעבור:
      גודל קטן, פאביקון, היפוך על מילוי, ומונוכרום. בסוף העמוד — פונט הכותרות,
      שהוא גם הפונט של הוורדמארק.</p>
    <nav class="jump">{jump}</nav>
  </div>
  {blocks}
  <p class="foot">הסימנים נוצרים ב-<code>brand/logo/logos.py</code> מתוך
    <code>brand/palette/directions.json</code> — הצבעים נקראים, לא הוקלדו.
    קבצי ה-SVG הבודדים ב-<code>brand/logo/marks/</code>.
    הסימנים והפונטים מוצגים תמיד על רקע לבן, גם במצב כהה, כי זה הרקע שעליו
    הם באמת ישבו.</p>
</div>"""

if __name__ == "__main__":
    import os
    os.makedirs("marks", exist_ok=True)
    for key, _t, fn, _w, _n in MARKS:
        io.open(f"marks/{key}.svg", "w", encoding="utf-8").write(
            svg(fn(C["brand"], C["accent"])))
        io.open(f"marks/{key}-mono.svg", "w", encoding="utf-8").write(
            svg(fn(C["inkStrong"], C["inkStrong"])))
    io.open("logos.html", "w", encoding="utf-8").write(HTML)
    print(f"{len(MARKS) * 2} svg files + logos.html ({len(HTML)} bytes)")
