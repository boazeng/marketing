# -*- coding: utf-8 -*-
"""
The one-pager: a single A4 page to send a prospect after a call.

Not a print of the website. A one-pager is read in forty seconds by someone
deciding whether to book a meeting, so it is an editorial condensation of
`content/messaging.md` -- shorter sentences, fewer claims, one action. The
markdown stays the source of truth for what we are allowed to say; the
wording here is cut to fit.

Colours and the mark are read from `brand/`, never retyped.

    python onepager.py    -> onepager.html + onepager.pdf + onepager.png
"""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
C = next(
    d for d in json.load(
        io.open(os.path.join(ROOT, "brand", "palette", "directions.json"), encoding="utf-8"))
    if d["name"] == "bridge"
)["colors"]

MARK = io.open(os.path.join(ROOT, "assets", "logos", "mark-reverse.svg"),
               encoding="utf-8").read()

# ---------------------------------------------------------------- contact
# The one block to edit before sending this to anyone.
#
# While CONFIRMED is False the output is written as `onepager-DRAFT.*` and the
# footer carries a visible draft strip. A one-pager that reaches a real
# prospect with a dead address is worse than no one-pager, so the flag stays
# False until the mailbox has actually been sent a message and received it.
CONFIRMED = True

CONTACT = {
    "site": "yazam-il.com",
    "email": "office@yazam-il.com",  # forwards to Sharona via Cloudflare
    "phone": "054-2408152",          # שרונה
    "person": "שרונה · סמנכ“לית שיווק",
}

HEADLINE = "כל תקופת הבדק. במקום אחד."
SUB = ("מערכת אחת שמנהלת את הליקויים בכל הפרויקטים שלך — מהרגע שהדייר "
       "מדווח ועד שהתקלה נסגרת, מתועדת וחתומה.")

PAIN = [
    ("תקלות נופלות בין הכיסאות", "אף אחד לא יודע כמה פתוחות עכשיו ומי בפיגור."),
    ("אין תיעוד", "כשמגיעה טענה שנה אחרי המסירה, אין מה להראות."),
    ("הדייר לא יודע מה קורה", "ולכן מתקשר שוב ושוב — זה הזמן של מנהל השירות."),
]

STEPS = [
    ("resident", "הדייר מדווח בעצמו",
     "קישור או QR לדירה. בלי הורדה ובלי סיסמה. הפנייה נכנסת כתקלה שממתינה לאישורך."),
    ("field", "המפקח סוגר מהשטח",
     "סטטוס, תמונות, יומן טיפול וחתימה על פרוטוקול — מהטלפון, בלי לחזור למשרד."),
    ("ai", "דוח הבדק נקרא לבד",
     "מעלים את ה-PDF, וסוכן AI מכניס את הליקויים מסווגים ומוכנים לאישור."),
]

FEATURES = [
    ("מבנה פרויקט הירארכי", "בניין ← כניסה ← קומה ← יחידת ממכר."),
    ("קישור אישי לבעל מקצוע", "רואה רק את התקלות שלו. בלי התחברות."),
    ("פרוטוקול מסירה חתום", "חתימה דיגיטלית של הדייר, שמורה ב-PDF."),
    ("דוחות להדפסה", "לפי פרויקט, סטטוס, בעל מקצוע ותאריך."),
]

PROOF = [
    ("פרויקט ראשון באותו יום", "מקימים מבנה פרויקט ומתחילים לעבוד — בלי פרויקט הטמעה."),
    ("הנתונים שלך בלבד", "כל חברה רואה רק את שלה. מסד נתונים פרטי ב-AWS פרנקפורט."),
    ("יומן פעילות מלא", "כל שינוי סטטוס, כל תמונה וכל הערה נשמרים עם חותמת זמן."),
]

APPS = [
    ("ליזם", "דפדפן", "כל הפרויקטים, ניהול מלא, דוחות והרשאות."),
    ("לאיש החברה", "אפליקציה", "סקירה, תקלות, פרוטוקולים ודוחות — מהשטח."),
    ("לדייר", "אפליקציה", "התקלות של הדירה ודיווח תקלה חדשה."),
]

GLYPHS = {
    "resident": "M3 11 12 4l9 7M5 10v9h14v-9M10 19v-5h4v5",
    "field": "M7 3h10a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1ZM11 18h2",
    "ai": "M8 3h6l4 4v14H6V5a2 2 0 0 1 2-2ZM14 3v4h4M9 13h6M9 17h4",
    "check": "M4 12.5 9 17.5 20 6.5",
    "alert": "M12 3 2 20h20L12 3ZM12 10v5M12 17.5v.5",
}


def icon(name, size=20):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round"><path d="{GLYPHS[name]}"/></svg>')


CSS = f"""
@page {{ size: A4; margin: 0; }}

@import url("https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700&family=Rubik:wght@700;800&family=Space+Grotesk:wght@500;700&display=swap");

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ direction: rtl; }}
body {{
  width: 210mm; height: 297mm;
  font-family: Heebo, "Segoe UI", sans-serif;
  font-size: 9.4pt; line-height: 1.42;
  color: {C['inkStrong']}; background: #fff;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
  display: flex; flex-direction: column;
}}
.pad {{ padding: 0 14mm; }}

/* ------------------------------------------------------------- masthead */
.top {{
  background: {C['brand']}; color: #fff;
  padding: 8mm 14mm 7.5mm;
  display: flex; flex-direction: column; gap: 4.5mm;
}}
.top-row {{ display: flex; align-items: center; justify-content: space-between; gap: 6mm; }}
.logo {{ display: flex; align-items: center; gap: 3mm; }}
.logo svg {{ width: 12mm; height: 12mm; }}
.logo-txt {{ display: flex; flex-direction: column; gap: 0.4mm; }}
.logo-grp {{
  font-family: "Space Grotesk", monospace; font-size: 7pt; font-weight: 500;
  letter-spacing: .24em; direction: ltr; unicode-bidi: isolate;
}}
.logo-grp i {{ font-style: normal; color: {C['accent']}; }}
.logo-word {{ font-family: Rubik, Heebo, sans-serif; font-weight: 800; font-size: 19pt; line-height: 1; }}
.top-for {{
  font-size: 8pt; letter-spacing: .04em;
  border: 0.35mm solid rgba(255,255,255,.42); border-radius: 2mm; padding: 1.4mm 3.2mm;
}}
h1 {{
  font-family: Rubik, Heebo, sans-serif; font-weight: 800;
  font-size: 25pt; line-height: 1.08; letter-spacing: -.025em;
}}
.sub {{ font-size: 10pt; color: rgba(255,255,255,.9); max-width: 122mm; }}

/* ---------------------------------------------------------------- pain */
.pain {{
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm;
  background: {C['mist']}; padding: 5mm 14mm;
}}
.pain-item {{ display: flex; gap: 2.4mm; align-items: flex-start; }}
.pain-item > div {{ flex: 1; min-width: 0; }}
.pain-item svg {{ flex: none; color: {C['accentDeep']}; margin-top: .4mm; }}
.pain-item b {{ display: block; font-size: 9.2pt; }}
.pain-item span {{ color: {C['inkSoft']}; font-size: 8.5pt; }}

/* --------------------------------------------------------------- blocks */
.block {{ padding-top: 6.5mm; }}
h2 {{
  font-family: Rubik, Heebo, sans-serif; font-weight: 700; font-size: 12.5pt;
  letter-spacing: -.015em; margin-bottom: 3.5mm;
}}
.steps {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; list-style: none; }}
.step {{
  position: relative; border: 0.3mm solid {C['border']}; border-radius: 3mm;
  padding: 4.5mm 4mm 4mm; display: flex; flex-direction: column; gap: 2mm;
}}
.step-n {{
  position: absolute; top: 3.4mm; inset-inline-end: 4mm;   /* RTL needs this stated */
  font-family: "Space Grotesk", monospace; font-size: 8pt; font-weight: 700;
  color: {C['accent']};
}}
.step-i {{
  width: 9mm; height: 9mm; border-radius: 2.4mm; background: {C['brand']}; color: #fff;
  display: flex; align-items: center; justify-content: center;
}}
.step b {{ font-size: 9.8pt; }}
.step span {{ color: {C['inkSoft']}; font-size: 8.5pt; }}

.feats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 2.6mm 6mm; list-style: none; }}
.feat {{ display: flex; gap: 2.4mm; align-items: flex-start; }}
.feat > div {{ flex: 1; min-width: 0; }}
.feat svg {{ flex: none; color: {C['brand']}; margin-top: .3mm; }}
.feat b {{ display: block; font-size: 9.2pt; }}
.feat span {{ color: {C['inkSoft']}; font-size: 8.5pt; }}

.apps {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; list-style: none; }}
.app {{ background: {C['brandSoft']}; border-radius: 3mm; padding: 3.6mm 4mm; }}
.app-who {{
  font-size: 8pt; font-weight: 500; color: {C['accentDeep']};
  display: block; margin-bottom: .8mm;
}}
.app b {{ font-size: 9.6pt; color: {C['brandInk']}; display: block; }}
.app span {{ font-size: 8.4pt; color: {C['inkSoft']}; }}

/* Stated plainly rather than buried -- promising Android before it exists is
   the fastest way to lose a developer's trust on the follow-up call. */
.note {{
  margin-top: 3mm; background: {C['accentSoft']}; border-radius: 2.4mm;
  padding: 2.6mm 3.4mm; font-size: 8.2pt; color: {C['inkSoft']};
}}

.proof {{
  margin-top: auto; display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 5mm; padding: 6mm 14mm 6.5mm; border-top: 0.3mm solid {C['border']};
}}
.proof-item {{ display: flex; gap: 2.4mm; align-items: flex-start; }}
.proof-item > div {{ flex: 1; min-width: 0; }}
.proof svg {{ flex: none; color: {C['brand']}; margin-top: .3mm; }}
.proof b {{ display: block; font-size: 9pt; }}
.proof span {{ font-size: 8.3pt; color: {C['inkSoft']}; }}

/* --------------------------------------------------------------- footer */
.foot {{
  background: {C['brandInk']}; color: #fff;
  padding: 6mm 14mm; display: flex; align-items: center;
  justify-content: space-between; gap: 6mm;
}}
.foot-cta b {{ font-family: Rubik, Heebo, sans-serif; font-weight: 700; font-size: 13pt; display: block; }}
.foot-cta span {{ font-size: 8.8pt; color: rgba(255,255,255,.72); }}
.foot-contact {{ text-align: end; font-size: 9pt; display: flex; flex-direction: column; gap: 1mm; }}
.foot-contact .ltr {{ font-family: "Space Grotesk", monospace; direction: ltr; unicode-bidi: isolate; }}
.foot-contact .site {{ font-weight: 700; font-size: 10.5pt; color: {C['accent']}; }}
.foot-person {{ color: rgba(255,255,255,.72); }}
.draft {{
  background: {C['accentDeep']}; color: #fff; text-align: center;
  font-size: 8pt; letter-spacing: .05em; padding: 1.8mm 14mm;
}}
"""


def build():
    pain = "".join(
        f'<div class="pain-item">{icon("alert", 17)}<div><b>{t}</b>'
        f'<span>{d}</span></div></div>' for t, d in PAIN)
    steps = "".join(
        f'<li class="step"><span class="step-n">{i + 1}</span>'
        f'<span class="step-i">{icon(k, 21)}</span><b>{t}</b><span>{d}</span></li>'
        for i, (k, t, d) in enumerate(STEPS))
    feats = "".join(
        f'<li class="feat">{icon("check", 16)}<div><b>{t}</b><span>{d}</span></div></li>'
        for t, d in FEATURES)
    proof = "".join(
        f'<div class="proof-item">{icon("check", 16)}<div><b>{t}</b>'
        f'<span>{d}</span></div></div>'
        for t, d in PROOF)
    apps = "".join(
        f'<li class="app"><span class="app-who">{who}</span><b>{what}</b>'
        f'<span>{d}</span></li>' for who, what, d in APPS)

    draft = "" if CONFIRMED else (
        '<div class="draft">טיוטה — פרטי הקשר עדיין לא סופיים. לא לשליחה ללקוח.</div>')

    rows = [f'<span class="site ltr">{CONTACT["site"]}</span>']
    if CONTACT["phone"]:
        rows.append(f'<span class="ltr">{CONTACT["phone"]}</span>')
    rows.append(f'<span class="ltr">{CONTACT["email"]}</span>')
    if CONTACT["person"]:
        rows.append(f'<span class="foot-person">{CONTACT["person"]}</span>')

    return f"""<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<title>TACT בדק — ניהול ליקויי בנייה</title>
<style>{CSS}</style></head><body>

<header class="top">
  <div class="top-row">
    <span class="logo">{MARK}<span class="logo-txt">
      <span class="logo-grp">T<i>·</i>A<i>·</i>C<i>·</i>T</span>
      <span class="logo-word">בדק</span></span></span>
    <span class="top-for">ליזמים וקבלני בנייה</span>
  </div>
  <h1>{HEADLINE}</h1>
  <p class="sub">{SUB}</p>
</header>

<section class="pain">{pain}</section>

<div class="pad">
  <section class="block">
    <h2>שלושה דברים שקורים בלעדיך</h2>
    <ol class="steps">{steps}</ol>
  </section>

  <section class="block">
    <h2>מה עוד יש בפנים</h2>
    <ul class="feats">{feats}</ul>
  </section>

  <section class="block">
    <h2>שלושה ממשקים, מערכת אחת</h2>
    <ul class="apps">{apps}</ul>
    <p class="note">האפליקציות לנייד עובדות כרגע על אייפון; גרסת אנדרואיד
      בפיתוח. הדייר בכל מקרה לא חייב אפליקציה — הקישור נפתח בדפדפן בכל מכשיר.</p>
  </section>
</div>

<section class="proof">{proof}</section>

<footer class="foot">
  <div class="foot-cta">
    <b>הדגמה של עשרים דקות, בלי מצגת</b>
    <span>נעלה פרויקט אחד שלך למערכת ותראה איך זה נראה.</span>
  </div>
  <div class="foot-contact">{"".join(rows)}</div>
</footer>
{draft}

</body></html>"""


if __name__ == "__main__":
    stem = "onepager" if CONFIRMED else "onepager-DRAFT"
    html = build()
    io.open(os.path.join(HERE, stem + ".html"), "w", encoding="utf-8").write(html)

    from playwright.sync_api import sync_playwright

    url = "file:///" + os.path.join(HERE, stem + ".html").replace("\\", "/")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 794, "height": 1123})
        pg.goto(url, wait_until="networkidle")
        pg.wait_for_timeout(1800)          # webfonts must land before we measure
        over = pg.evaluate("document.body.scrollHeight - document.body.clientHeight")
        pg.pdf(path=os.path.join(HERE, stem + ".pdf"),
               format="A4", print_background=True,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        pg.screenshot(path=os.path.join(HERE, stem + ".png"), full_page=True)
        b.close()

    # A one-pager that silently becomes a two-pager is the whole failure mode.
    if over > 2:
        print(f"OVERFLOW: content exceeds A4 by {over}px -- trim before sending.")
        sys.exit(1)
    print(f"{stem}.html + .pdf + .png   (fits A4, overflow {over:+d}px)")
    if not CONFIRMED:
        print("DRAFT: contact details are unconfirmed, so the files are named")
        print("       onepager-DRAFT.* and the page carries a draft strip.")
        print("       Set CONFIRMED = True once the phone and mailbox are real.")
