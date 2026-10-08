# -*- coding: utf-8 -*-
"""
The ads: copy and images from one list.

    python ads.py            -> social/out/ad-<n>-<format>.png, every ad in every
                                Facebook placement size (see FORMATS)
    python ads.py --copy     print the copy only
                             (a full run also writes out/ads-approved.pdf: each
                             image beside its text, the record of what was approved)

ADS is the single source for both the picture and the text Meta shows around
it, so the campaign builder imports it from here. A headline fixed in the
image but not in the ad text is the kind of drift that gets an unapproved
wording published.

The brief (Boaz, 2026-10-05): very short, formal, and with one job -- get the
click through to the landing page. So no price, no superlatives, no urgency,
and nothing that addresses the reader's own age or health: Meta rejects that
(personal attributes) and the bar's advertising rules frown on the rest.
Every factual claim here already appears on the landing page the lawyer
reviewed; an ad must not say more than the page it leads to.
"""
import base64, os, sys

sys.stdout.reconfigure(encoding="utf-8")

from assets import MARK, NAME, NAVY, NAVY_DEEP, GOLD, GOLD_SOFT, OUT

URL = "https://zohar.newavera.co.il"
CTA = "LEARN_MORE"
CREAM, INK = "#f7f4ef", "#1c2a3a"
APPROVED_ON = "5.10.2026"

# Approved by the lawyer 2026-10-05 (relayed by Boaz), all four as worded here.
# A fifth, "נערך בפני עורך דין. מופקד אצל האפוטרופוס הכללי.", was rejected --
# do not bring it back in another form without asking.
# Any change to a word below needs a new approval before it is published.
#
# image: (eyebrow, headline, line under it) -- <br> breaks the headline where
#        it should break, not where the browser decides.
# primary: the text above the image. headline: the bold line beside the button.
ADS = [
    dict(key="what", theme="navy",
         image=("ייפוי כוח מתמשך", "קובעים מראש<br>מי יחליט בשמכם",
                "מסמך משפטי אחד, שנערך בפני עורך דין."),
         primary="ייפוי כוח מתמשך מאפשר לקבוע מראש מי יטפל בענייניכם, אם לא תוכלו להחליט בעצמכם.",
         headline="ייפוי כוח מתמשך — מה זה ואיך עורכים"),
    dict(key="guardian", theme="cream",
         image=("ייפוי כוח מתמשך", "במקום מינוי אפוטרופוס<br>בבית המשפט",
                "האדם וההוראות נקבעים מראש, על ידכם."),
         primary="במקום מינוי אפוטרופוס דרך בית המשפט — קובעים מראש את האדם ואת ההוראות.",
         headline="ייפוי כוח מתמשך: החלופה לאפוטרופסות"),
    dict(key="three", theme="navy",
         image=("מה מסדירים בייפוי כוח מתמשך", "עניינים אישיים,<br>רפואיים ורכושיים",
                "שלושה תחומים, מסמך אחד."),
         primary="עניינים אישיים, רפואיים ורכושיים — מוסדרים מראש במסמך אחד.",
         headline="מה אפשר להסדיר בייפוי כוח מתמשך"),
    dict(key="adult", theme="cream",
         image=("ייפוי כוח מתמשך", "לא רק<br>לגיל השלישי",
                "כל אדם בגיר וכשיר רשאי לערוך אותו."),
         primary="ייפוי כוח מתמשך אינו מיועד רק לגיל השלישי. כל אדם בגיר וכשיר רשאי לערוך אותו.",
         headline="למי מתאים ייפוי כוח מתמשך"),
]

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Heebo:wght@400;500;800&display=swap">')

THEMES = {
    "navy": dict(bg=f"radial-gradient(ellipse 80% 60% at 100% 0%, rgba(196,163,90,.20), transparent 55%),"
                    f"linear-gradient(145deg, {NAVY_DEEP} 0%, {NAVY} 55%, #163a5f 100%)",
                 head="#ffffff", sub="rgba(255,255,255,.84)", accent=GOLD_SOFT,
                 rule=GOLD, foot="rgba(255,255,255,.2)"),
    "cream": dict(bg=CREAM, head=NAVY, sub="#3d4d5f", accent="#8a6d24",
                  rule=GOLD, foot="rgba(15,39,68,.16)"),
}


# name: (width, height, padding top/side/bottom, type scale, where Meta shows it)
# One message, four canvases: Meta crops a single image to fit each placement,
# and a crop of a text image cuts the text. Each placement gets its own render.
FORMATS = {
    "1x1":    (1080, 1080, (96, 92, 84),   1.00, "פיד — ריבוע"),
    "4x5":    (1080, 1350, (120, 92, 100), 1.08, "פיד בנייד — הגודל שתופס הכי הרבה מסך"),
    # Stories and Reels draw the profile bar over the top ~14% and the button
    # and caption over the bottom ~20%; the padding keeps every word out of both.
    "9x16":   (1080, 1920, (290, 92, 400), 1.15, "סטורי ורילס"),
    "191x100": (1200, 628, (48, 76, 40),   0.60, "עמודה ימנית ותצוגת קישור — לרוחב"),
}


def html(ad, fmt="1x1"):
    t = THEMES[ad["theme"]]
    w, h, (pt, ps, pb), k, _ = FORMATS[fmt]
    eyebrow, head, sub = ad["image"]
    # Long headlines step down a size rather than wrap into a third line.
    longest = max(len(p) for p in head.split("<br>"))
    size = next(px for limit, px in ((12, 124), (16, 100), (19, 82), (99, 72))
                if longest <= limit)
    px = lambda n: f"{round(n * k)}px"
    return f"""<!doctype html><meta charset="utf-8">{FONTS}
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{width:{w}px;height:{h}px;overflow:hidden;direction:rtl;
    font-family:Heebo,sans-serif;-webkit-font-smoothing:antialiased}}
  body{{background:{t['bg']};padding:{pt}px {ps}px {pb}px;display:flex;flex-direction:column}}
  /* the subject line: bold and large enough to be read first (Boaz, 2026-10-05) */
  .eyebrow{{font-size:{px(50)};font-weight:800;color:{t['accent']}}}
  .rule{{width:{px(108)};height:{px(6)};border-radius:3px;background:{t['rule']};margin-top:{px(26)}}}
  /* the message sits in the middle of the canvas, where the eye lands in a feed */
  .main{{flex:1;display:flex;flex-direction:column;justify-content:center}}
  h1{{font-size:{px(size)};font-weight:800;line-height:1.2;letter-spacing:-.02em;color:{t['head']}}}
  .sub{{font-size:{px(46)};line-height:1.45;color:{t['sub']};margin-top:{px(44)}}}
  .foot{{padding-top:{px(38)};border-top:2px solid {t['foot']};
    display:flex;align-items:center;gap:{px(26)}}}
  .foot svg{{width:{px(84)};height:{px(84)};flex:none;color:{t['accent']}}}
  .who{{font-size:{px(40)};font-weight:500;color:{t['head']}}}
</style>
<div class="eyebrow">{eyebrow}</div>
<div class="rule"></div>
<div class="main"><h1>{head}</h1>
<p class="sub">{sub}</p></div>
<div class="foot">{MARK}<span class="who">{NAME}</span></div>"""


def show_copy():
    for i, ad in enumerate(ADS, 1):
        eyebrow, head, sub = ad["image"]
        print(f"מודעה {i}")
        print(f"  טקסט מעל התמונה:  {ad['primary']}")
        print(f"  על התמונה:        {head.replace('<br>', ' ')} / {sub}")
        print(f"  כותרת ליד הכפתור: {ad['headline']}")
        print(f"  כפתור:            למידע נוסף -> {URL}\n")


def approval_html(paths):
    """Markdown shows as raw text in SharePoint, so the record is a PDF."""
    rows = ""
    for i, (ad, path) in enumerate(zip(ADS, paths), 1):
        img = base64.b64encode(open(path, "rb").read()).decode()
        rows += f"""<section><img src="data:image/png;base64,{img}">
<div><h2>מודעה {i}</h2>
<dl><dt>טקסט מעל התמונה</dt><dd>{ad['primary']}</dd>
<dt>כותרת ליד הכפתור</dt><dd>{ad['headline']}</dd>
<dt>כפתור</dt><dd>למידע נוסף ← <span dir="ltr">{URL}</span></dd></dl>
</div></section>"""
    return f"""<!doctype html><meta charset="utf-8">{FONTS}
<style>
  @page{{size:A4;margin:14mm}}
  body{{font-family:Heebo,sans-serif;direction:rtl;color:{INK};font-size:11pt}}
  h1{{font-size:17pt;color:{NAVY}}} .lead{{color:#5a6b7d;margin:2mm 0 5mm}}
  section{{display:flex;gap:7mm;align-items:flex-start;padding:4mm 0;
    border-top:1px solid #d9d4ca;break-inside:avoid}}
  img{{width:62mm;height:62mm;flex:none;border:1px solid #d9d4ca}}
  h2{{font-size:12.5pt;color:{NAVY};margin-bottom:2mm}}
  dt{{font-size:8.5pt;color:#8a6d24;font-weight:500;margin-top:2.2mm}} dd{{margin:0}}
  .ok{{margin-top:4mm;font-size:10pt}}
</style>
<h1>מודעות פייסבוק מאושרות — ייפוי כוח מתמשך</h1>
<p class="lead">אושרו על ידי {NAME} ב-{APPROVED_ON}. כל המודעות מובילות לדף הנחיתה.<br>
שינוי בנוסח מחייב אישור חדש.<br>
כל מודעה מיוצרת בארבעה גדלים לפי מיקום ההצגה ({" · ".join(f"{v[0]}×{v[1]}" for v in FORMATS.values())}); הנוסח זהה בכולם.</p>
{rows}"""


if __name__ == "__main__":
    if "--copy" in sys.argv:
        show_copy()
        sys.exit(0)

    from playwright.sync_api import sync_playwright
    from PIL import Image

    os.makedirs(OUT, exist_ok=True)
    made = {f: [] for f in FORMATS}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for fmt, (w, h, *_rest) in FORMATS.items():
            for i, ad in enumerate(ADS, 1):
                pg = b.new_page(viewport={"width": w, "height": h},
                                device_scale_factor=1)
                pg.set_content(html(ad, fmt))
                pg.wait_for_timeout(1500)      # webfonts must land before capture
                # Text that overflows the canvas is clipped silently; fail instead.
                if pg.evaluate("[document.body.scrollHeight, document.body.scrollWidth]") != [h, w]:
                    raise SystemExit(f"ad {i} ({ad['key']}) {fmt}: text overflows the image")
                made[fmt].append(os.path.join(OUT, f"ad-{i}-{fmt}.png"))
                pg.screenshot(path=made[fmt][-1])
                pg.close()
            print(f"   {fmt:8} {w}x{h}  x{len(ADS)}")
        b.close()
    paths = made["1x1"]

    # One sheet per format to judge them side by side; underscore = not a deliverable.
    for fmt, files in made.items():
        w, h = FORMATS[fmt][:2]
        tw, th, gap = 432, round(432 * h / w), 14
        sheet = Image.new("RGB", (len(files) * (tw + gap) - gap, th), "white")
        for i, path in enumerate(files):
            sheet.paste(Image.open(path).resize((tw, th)), (i * (tw + gap), 0))
        try:
            sheet.save(os.path.join(OUT, f"_sheet-{fmt}.png"))
        except OSError:
            # Windows refuses the write while an image viewer holds the file open.
            # The sheet is only a convenience; the deliverables still matter.
            print(f"   !! _sheet-{fmt}.png is open in a viewer -- not refreshed")

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(approval_html(paths))
        pg.wait_for_timeout(2000)
        pg.pdf(path=os.path.join(OUT, "ads-approved.pdf"), format="A4",
               print_background=True)
        b.close()
    print("   ads-approved.pdf")
    print(f"\n-> {OUT}")
