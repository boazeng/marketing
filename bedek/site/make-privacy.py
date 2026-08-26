# -*- coding: utf-8 -*-
"""
Generates public/privacy.html from the palette.

A static page rather than a React route, for the same reason as 404.html: it
has to render even when the bundle does not, and a regulator or a curious
buyer should never meet a blank screen here.

The text describes what the site ACTUALLY does -- one analytics pixel behind
consent, and a lead form -- rather than the boilerplate that claims a dozen
processors nobody can name. If the site's behaviour changes, this changes.

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

SECTIONS = [
    ("מי אנחנו", """<p>האתר מופעל על ידי <b>TACT NIRIM</b>. לשאלות בנושא פרטיות:
       <a class="ltr" href="mailto:office@yazam-il.com">office@yazam-il.com</a>.</p>"""),
    ("איזה מידע נאסף", """
       <p><b>מה שאתה מוסר בטופס.</b> שם, חברה, טלפון, אימייל, ומה שכתבת בשדה
       ההערות. נאסף רק אם מילאת ושלחת את הטופס.</p>
       <p><b>מאיזה קמפיין הגעת.</b> אם הגעת דרך מודעה, הכתובת מכילה מזהי
       קמפיין (<span class="ltr">utm</span>) שנשמרים יחד עם הפנייה.</p>
       <p><b>מדידה אנונימית</b> — רק אם אישרת עוגיות. ראה למטה.</p>"""),
    ("מה עושים במידע", """
       <p>הפנייה נשמרת במערכת ניהול הלקוחות שלנו ומשמשת <b>אך ורק</b> כדי לחזור
       אליך בנוגע לפנייה. איננו מוכרים מידע, ואיננו מעבירים אותו לצד שלישי
       למטרות שיווק.</p>"""),
    ("עוגיות", """
       <p>האתר טוען <b>פיקסל של Meta</b> אחד, ורק אחרי שאישרת. הוא מודד כמה
       אנשים הגיעו מכל מודעה וכמה מהם השאירו פנייה.</p>
       <p><b>אם לא אישרת — הוא לא נטען כלל,</b> והאתר עובד בדיוק אותו דבר.
       בחירתך נשמרת בדפדפן שלך (<span class="ltr">localStorage</span>) ואינה
       נשלחת לשום מקום. לשינוי — נקה את נתוני האתר בדפדפן והבאנר יופיע שוב.</p>"""),
    ("איפה המידע נשמר", """
       <p>האתר מתארח ב-<b>AWS</b>. פניות מהטופס נשמרות במערכת שלנו, גם היא
       ב-AWS. תעבורת האתר עוברת דרך <b>Cloudflare</b> (שירותי DNS) ודואר
       נכנס לכתובות הדומיין מנותב דרכה.</p>"""),
    ("הזכויות שלך", """
       <p>אתה רשאי לבקש לראות איזה מידע שמור עליך, לתקן אותו, או לבקש שיימחק.
       פנה לכתובת שלמעלה ונטפל בכך.</p>"""),
]

HTML = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>מדיניות פרטיות · TACT בדק</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700&family=Rubik:wght@700;800&family=Space+Grotesk:wght@500&display=swap">
<style>
  *,*::before,*::after {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: {C['canvas']}; color: {C['inkStrong']};
    font-family: Heebo, "Segoe UI", system-ui, sans-serif; line-height: 1.7;
  }}
  .wrap {{ max-width: 760px; margin: 0 auto; padding: 48px 24px 80px; }}
  header {{ display: flex; align-items: center; gap: 12px;
    padding-bottom: 26px; border-bottom: 1px solid {C['border']}; }}
  header svg {{ width: 40px; height: 40px; }}
  .name {{ font-family: Rubik, Heebo, sans-serif; font-weight: 800;
    font-size: 24px; color: {C['brand']}; }}
  h1 {{ font-family: Rubik, Heebo, sans-serif; font-weight: 800;
    font-size: clamp(28px, 5vw, 40px); letter-spacing: -.022em;
    margin: 34px 0 6px; }}
  .upd {{ color: {C['inkFaint']}; font-size: 14px; margin: 0 0 8px; }}
  h2 {{ font-family: Rubik, Heebo, sans-serif; font-weight: 700; font-size: 19px;
    margin: 34px 0 8px; color: {C['brandInk']}; }}
  p {{ margin: 0 0 12px; max-width: 62ch; color: {C['inkSoft']}; }}
  b {{ color: {C['inkStrong']}; }}
  a {{ color: {C['brand']}; text-underline-offset: 3px; }}
  .ltr {{ direction: ltr; unicode-bidi: isolate;
    font-family: "Space Grotesk", monospace; }}
  .back {{ display: inline-block; margin-top: 40px; padding-top: 22px;
    border-top: 1px solid {C['border']}; width: 100%; font-weight: 500; }}
</style>
</head>
<body>
  <div class="wrap">
    <header>{MARK}<span class="name">בדק</span></header>
    <h1>מדיניות פרטיות</h1>
    <p class="upd">עודכן: אוגוסט 2026</p>
    {''.join(f'<h2>{t}</h2>{b}' for t, b in SECTIONS)}
    <a class="back" href="/">חזרה לאתר</a>
  </div>
</body>
</html>
"""

if __name__ == "__main__":
    out = os.path.join(HERE, "public", "privacy.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, "w", encoding="utf-8").write(HTML)
    print("   public/privacy.html")
