# -*- coding: utf-8 -*-
"""
The chosen mark, built out into a usable kit.

Direction ג' -- the closing loop -- picked 2026-08-25. This script owns the
mark's geometry from here on; logos.py keeps the five candidates only as the
record of what was considered.

    python kit.py    -> ../../assets/logos/*.svg  +  logo-kit.html
"""
import io, json, math, os, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "logos"))
PAL = json.load(io.open(os.path.join(HERE, "..", "palette", "directions.json"),
                        encoding="utf-8"))
C = next(d for d in PAL if d["name"] == "bridge")["colors"]

VB = 64.0
R, DOT, STROKE = 21.0, 6.0, 7.0
BREAK = 305.0          # not 270 -- see mark() below
CLEAR = DOT * 2        # clear space on every side, in grid units


def mark(ring, bead, stroke=STROKE):
    """The lifecycle of a defect closing: reported, assigned, fixed, signed.

    Two constraints hold this shape together and neither is decorative. The
    arc caps stop exactly where the bead begins -- zero clearance -- so the
    bead reads as the piece that shuts the ring rather than as something
    floating above it. And the break sits at 305 degrees: a power glyph is
    always symmetrical about the vertical axis, so putting the break on that
    axis made the whole mark read as an on/off button. 305 also happens to be
    where an RTL eye enters a circle.
    """
    cx = cy = VB / 2
    half = math.degrees(math.atan(DOT / R)) + math.degrees(math.atan(stroke / 2 / R))
    a0, a1 = math.radians(BREAK + half), math.radians(BREAK - half)
    p0 = (cx + R * math.cos(a0), cy + R * math.sin(a0))
    p1 = (cx + R * math.cos(a1), cy + R * math.sin(a1))
    pb = (cx + R * math.cos(math.radians(BREAK)), cy + R * math.sin(math.radians(BREAK)))
    return (f'<path d="M{p0[0]:.2f} {p0[1]:.2f} A{R} {R} 0 1 1 {p1[0]:.2f} {p1[1]:.2f}" '
            f'fill="none" stroke="{ring}" stroke-width="{stroke}" stroke-linecap="round"/>'
            f'<circle cx="{pb[0]:.2f}" cy="{pb[1]:.2f}" r="{DOT}" fill="{bead}"/>')


def svg(inner, size=None, bg=None, rx=0, pad=0.0):
    """`pad` widens the viewBox symmetrically -- used for the app icon, where
    the mark needs breathing room inside the squircle."""
    lo, span = -pad, VB + pad * 2
    dim = f' width="{size}" height="{size}"' if size else ""
    ground = f'<rect x="{lo}" y="{lo}" width="{span}" height="{span}" rx="{rx}" fill="{bg}"/>' if bg else ""
    return (f'<svg viewBox="{lo} {lo} {span} {span}"{dim} '
            f'xmlns="http://www.w3.org/2000/svg" role="img">{ground}{inner}</svg>')


VARIANTS = {
    "mark":         svg(mark(C["brand"], C["accent"])),
    "mark-mono":    svg(mark(C["inkStrong"], C["inkStrong"])),
    "mark-reverse": svg(mark("#FFFFFF", C["accent"])),
    "mark-white":   svg(mark("#FFFFFF", "#FFFFFF")),
    "app-icon":     svg(mark("#FFFFFF", C["accent"]), bg=C["brand"], rx=20, pad=13),
    # heavier stroke: at 32px a 7-unit ring thins out to nothing
    "favicon":      svg(mark(C["brand"], C["accent"], 8.0), size=32),
}


def wordmark(face, weight, brand, accent, scale=1.0):
    return f"""<span class="wm" style="--s:{scale}">
  <span class="wm-tact" style="color:{brand}">T<i style="color:{accent}">·</i>A<i style="color:{accent}">·</i>C<i style="color:{accent}">·</i>T</span>
  <span class="wm-word" style="font-family:'{face}',Heebo,sans-serif;font-weight:{weight};color:{brand}">בדק</span>
</span>"""


FACES = [("Rubik", 800, "מומלץ — טווח משקלים מלא, כך שאותה משפחה עובדת בכותרת ובתווית"),
         ("Suez One", 400, "כובד סלאבי, משקל אחד — לכותרות בלבד"),
         ("Secular One", 400, "שחור וצפוף, משקל אחד — נשבר בכותרת בינונית")]

MISUSE = [
    ("אל תסובב", "הפתח חייב להישאר ב-305 מעלות. סיבוב לשעה 12 הופך את הסימן לכפתור הפעלה.",
     'style="transform:rotate(55deg)"'),
    ("אל תחליף את צבע הנקודה", "הענבר הוא האקסנט היחיד. נקודה בצבע המותג מוחקת את כל האמירה.", ""),
    ("אל תמתח", "יחס 1:1 בלבד.", 'style="transform:scaleX(1.35)"'),
    ("אל תוסיף מסגרת או צל", "הסימן שטוח. צל הופך אותו לאייקון של מישהו אחר.", ""),
]


def misuse_svg(i):
    """Each card has to *show* its mistake, not just name it."""
    if i == 1:                                    # dot recoloured to the brand
        return svg(mark(C["brand"], C["brand"]))
    if i == 3:                                    # boxed and dropshadowed
        return ('<span style="display:block;padding:4px;border:2px solid '
                + C["brandDeep"] + ';border-radius:7px;box-shadow:0 3px 5px '
                'rgba(0,0,0,.45);background:#fff">'
                + svg(mark(C["brand"], C["accent"])) + '</span>')
    return svg(mark(C["brand"], C["accent"]))


CSS = """
:root { --page:#F7F7F6; --panel:#FFFFFF; --ink:#1A1A19; --ink-2:#5F5F5B;
        --ink-3:#8A8A85; --rule:#E2E2DE; --rule-2:#EFEFEC; --bad:#B3261E; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --page:#131312; --panel:#1C1C1A; --ink:#EDEDEA;
    --ink-2:#A5A59F; --ink-3:#77776F; --rule:#2E2E2B; --rule-2:#242422; --bad:#F2836F; } }
:root[data-theme="dark"] { --page:#131312; --panel:#1C1C1A; --ink:#EDEDEA;
  --ink-2:#A5A59F; --ink-3:#77776F; --rule:#2E2E2B; --rule-2:#242422; --bad:#F2836F; }
*, *::before, *::after { box-sizing:border-box; }
html { direction:rtl; }
body { margin:0; background:var(--page); color:var(--ink);
       font-family:Heebo,"Segoe UI",system-ui,sans-serif; font-size:16px;
       line-height:1.6; -webkit-font-smoothing:antialiased; }
.wrap { max-width:1080px; margin:0 auto; padding:56px 24px 96px; }
.top { display:flex; flex-direction:column; gap:13px; padding-bottom:26px;
       border-bottom:1px solid var(--rule); }
.kicker { font-family:"Space Grotesk",ui-monospace,monospace; font-size:12px;
          letter-spacing:.14em; color:var(--ink-3); text-transform:uppercase; }
h1 { margin:0; font-size:clamp(30px,4.4vw,46px); font-weight:900;
     letter-spacing:-.022em; line-height:1.1; text-wrap:balance; }
.lede { margin:0; max-width:62ch; color:var(--ink-2); font-size:17px; }
:focus-visible { outline:2px solid var(--ink); outline-offset:2px; }

section { margin-top:46px; padding-top:24px; border-top:1px solid var(--rule); }
section:first-of-type { margin-top:30px; padding-top:0; border-top:0; }
h2 { margin:0 0 6px; font-size:21px; font-weight:700; letter-spacing:-.01em; }
.sub { margin:0 0 20px; font-size:14.5px; color:var(--ink-2); max-width:70ch; }

.hero { background:#FFFFFF; border:1px solid var(--rule); border-radius:14px;
        padding:52px 30px; display:grid; place-items:center; }
.lockup { display:flex; align-items:center; gap:20px; }
.lockup svg { width:76px; height:76px; display:block; }
.wm { display:flex; flex-direction:column; align-items:flex-start; gap:3px; }
.wm-tact { font-family:"Space Grotesk",monospace; font-weight:500;
           font-size:calc(13px * var(--s,1)); letter-spacing:.24em;
           direction:ltr; unicode-bidi:isolate; }
.wm-tact i { font-style:normal; }
.wm-word { font-size:calc(46px * var(--s,1)); line-height:1; letter-spacing:-.02em; }

.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:14px; }
.tile { background:#FFFFFF; border:1px solid var(--rule); border-radius:12px;
        padding:20px; display:flex; flex-direction:column; align-items:center; gap:11px; }
.tile.on-brand { background:%BRAND%; border-color:%BRAND%; }
.tile.on-ink { background:%INK%; border-color:%INK%; }
.tile svg { width:52px; height:52px; }
.tile b { font-family:"Space Grotesk",monospace; font-weight:500; font-size:11.5px;
          color:#8A8A85; }
.tile.on-brand b, .tile.on-ink b { color:rgba(255,255,255,.66); }

.sizes { display:flex; align-items:flex-end; gap:26px; flex-wrap:wrap;
         background:#FFFFFF; border:1px solid var(--rule); border-radius:12px; padding:26px; }
.sizes figure { margin:0; display:flex; flex-direction:column; align-items:center; gap:9px; }
.sizes figcaption { font-family:"Space Grotesk",monospace; font-size:11px; color:#8A8A85; }

.faces { display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:14px; }
.face { background:#FFFFFF; border:1px solid var(--rule); border-radius:12px; padding:22px;
        display:flex; flex-direction:column; gap:12px; }
.face-meta { font-size:12.5px; color:#5F5F5B; }
.face-meta b { font-family:"Space Grotesk",monospace; font-weight:500; }

.rules { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; }
.rule-card { background:var(--panel); border:1px solid var(--rule); border-radius:12px;
             padding:18px; display:flex; gap:14px; align-items:flex-start; }
.rule-card .bad { width:46px; height:46px; flex:none; display:grid; place-items:center;
                  background:#FFF; border-radius:9px; position:relative; overflow:hidden; }
.rule-card .bad svg { width:34px; height:34px; }
.rule-card .bad::after { content:""; position:absolute; inset:0;
  background:linear-gradient(to bottom right, transparent 47%, var(--bad) 47%,
             var(--bad) 53%, transparent 53%); }
.rule-card h3 { margin:0 0 3px; font-size:14px; font-weight:700; color:var(--bad); }
.rule-card p { margin:0; font-size:13px; color:var(--ink-2); }

.clear { background:#FFFFFF; border:1px solid var(--rule); border-radius:12px;
         padding:30px; display:grid; place-items:center; }
.clear .box { position:relative; padding:%CLEARPX%px; outline:1px dashed #B9C6CC; }
.clear svg { width:92px; height:92px; display:block; }

.files { width:100%; border-collapse:collapse; font-size:13.5px; }
.files th, .files td { text-align:start; padding:9px 12px; border-bottom:1px solid var(--rule); }
.files th { font-size:11px; letter-spacing:.1em; color:var(--ink-3); text-transform:uppercase;
            font-weight:500; }
.files code { font-family:"Space Grotesk",monospace; font-size:12.5px;
              background:var(--rule-2); border-radius:4px; padding:1px 6px; }
.scroll { overflow-x:auto; }
.foot { margin-top:52px; padding-top:20px; border-top:1px solid var(--rule);
        font-size:13.5px; color:var(--ink-2); }
.foot code { font-family:"Space Grotesk",monospace; font-size:12.5px;
             background:var(--rule-2); border-radius:4px; padding:1px 5px; }
"""

FILES = [
    ("mark.svg", "הסימן. שימוש ראשי על רקע בהיר."),
    ("mark-mono.svg", "מונוכרום — פקס, חריטה, מסמך בשחור־לבן."),
    ("mark-reverse.svg", "טבעת לבנה, נקודה בענבר — על מילוי כהה או על צילום."),
    ("mark-white.svg", "לבן מלא — כשגם הנקודה חייבת להיעלם ברקע."),
    ("app-icon.svg", "אייקון אפליקציה 1024×1024 — מילוי מותג, סימן הפוך."),
    ("favicon.svg", "פאביקון 32px — קו עבה יותר, כי בגודל הזה 7 יחידות נעלמות."),
]


def build_html():
    tiles = "".join(
        f'<div class="tile{cls}">{VARIANTS[k]}<b>{k}</b></div>'
        for k, cls in [("mark", ""), ("mark-mono", ""),
                       ("mark-reverse", " on-brand"), ("mark-white", " on-ink")])
    icons = f'<div class="tile">{VARIANTS["app-icon"]}<b>app-icon</b></div>'
    sizes = "".join(
        f'<figure><span style="display:block;width:{s}px;height:{s}px">'
        f'{svg(mark(C["brand"], C["accent"], 8.0 if s <= 24 else STROKE))}</span>'
        f'<figcaption>{s}px</figcaption></figure>'
        for s in (96, 56, 32, 24, 18))
    faces = "".join(
        f'<div class="face">{wordmark(f, w, C["brand"], C["accent"], .86)}'
        f'<div class="face-meta"><b>{f}</b> — {d}</div></div>'
        for f, w, d in FACES)
    rules = "".join(
        f'<div class="rule-card"><span class="bad"><span {t}>{misuse_svg(i)}</span></span>'
        f'<span><h3>{h}</h3><p>{p}</p></span></div>'
        for i, (h, p, t) in enumerate(MISUSE))
    files = "".join(
        f'<tr><td><code>{n}</code></td><td>{d}</td></tr>' for n, d in FILES)

    css = (CSS.replace("%BRAND%", C["brand"]).replace("%INK%", C["inkStrong"])
              .replace("%CLEARPX%", f"{92 * CLEAR / VB:.0f}"))

    return f"""<title>ערכת הסימן של בדק</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;900&family=Rubik:wght@500;700;800&family=Secular+One&family=Suez+One&family=Space+Grotesk:wght@400;500;700&display=swap">
<style>{css}</style>
<div class="wrap">
  <div class="top">
    <span class="kicker">TACT &middot; marketing/bedek</span>
    <h1>ערכת הסימן</h1>
    <p class="lede">כיוון ג׳ — <b>מעגל נסגר</b> — בפלטת א׳ גשר. מחזור החיים של
      התקלה: מדווחת, משויכת, מטופלת, חתומה; הנקודה בענבר היא מה שסוגר את
      הטבעת.</p>
  </div>

  <section>
    <h2>הנעילה הראשית</h2>
    <p class="sub">הסימן מימין, השם משמאלו. ‏TACT נעול ל-LTR תמיד, גם בתוך
      טקסט עברי, והנקודות בענבר הן אותו מכשיר גרפי של ‏T∙A∙C∙T — רק בצבע שלנו
      במקום בראסט של הקבוצה.</p>
    <div class="hero"><div class="lockup">{VARIANTS["mark"]}{wordmark("Rubik", 800, C["brand"], C["accent"])}</div></div>
  </section>

  <section>
    <h2>גרסאות</h2>
    <p class="sub">ארבע גרסאות של הסימן ואייקון האפליקציה. אין גרסה חמישית —
      אם נדרש משהו אחר, זה סימן שהרקע לא מתאים.</p>
    <div class="grid">{tiles}{icons}</div>
  </section>

  <section>
    <h2>גדלים</h2>
    <p class="sub">מתחת ל-24px עובי הקו עולה מ-7 ל-8 יחידות, אחרת הטבעת
      מתאדה. <b>18px הוא המינימום</b> — מתחתיו הנקודה והטבעת מתמזגות.</p>
    <div class="sizes">{sizes}</div>
  </section>

  <section>
    <h2>שטח נקי</h2>
    <p class="sub">מרווח בכל צד בגובה קוטר הנקודה ({CLEAR:.0f} מתוך 64 יחידות
      = {CLEAR / VB * 100:.0f}%). שום דבר לא נכנס לתוך המסגרת המקווקוות.</p>
    <div class="clear"><div class="box">{VARIANTS["mark"]}</div></div>
  </section>

  <section>
    <h2>פונט הכותרות — נותר להחליט</h2>
    <p class="sub">גוף הטקסט והממשק נשארים <b>Heebo</b>, כמו ב-TACT ובשתי
      האפליקציות; מספרים ואנגלית ב-<b>Space Grotesk</b>. מה שנותר הוא פונט
      הכותרות, שהוא גם הפונט של הוורדמארק. שלושתם ב-Google Fonts.</p>
    <div class="faces">{faces}</div>
  </section>

  <section>
    <h2>ארבע טעויות</h2>
    <p class="sub">כל אחת מהן ראיתי קורית בפועל בערכות דומות.</p>
    <div class="rules">{rules}</div>
  </section>

  <section>
    <h2>הקבצים</h2>
    <p class="sub">ב-<code>assets/logos/</code>. כולם נוצרים מ-<code>brand/logo/kit.py</code>
      — אם צריך גרסה נוספת, מוסיפים אותה שם ולא מייצאים ביד.</p>
    <div class="scroll"><table class="files">
      <thead><tr><th>קובץ</th><th>מתי</th></tr></thead><tbody>{files}</tbody>
    </table></div>
  </section>

  <p class="foot">הגאומטריה חיה ב-<code>brand/logo/kit.py</code>; הצבעים נקראים
    מ-<code>brand/palette/directions.json</code> ולא הוקלדו. הסימן מוצג תמיד על
    רקע לבן, גם במצב כהה, כי זה הרקע שעליו הוא באמת יושב.</p>
</div>"""


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, content in VARIANTS.items():
        io.open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8").write(content)
    io.open(os.path.join(HERE, "logo-kit.html"), "w", encoding="utf-8").write(build_html())
    print(f"{len(VARIANTS)} svg -> assets/logos/ + logo-kit.html")
