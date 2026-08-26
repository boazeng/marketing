# פלטות — ארבעה כיוונים

```bash
python palette.py     # OKLCH spec -> directions.json
python contrast.py    # WCAG AA gate — exit 1 על כל כשל
python preview.py     # directions.json -> preview.html
```

| קובץ | תפקיד |
|---|---|
| `oklch.py` | המרת OKLCH→sRGB + חישוב ניגודיות |
| `palette.py` | **מקור האמת** — מפרט ארבעת הכיוונים ב-OKLCH |
| `contrast.py` | 17 צמדים לכל כיוון, נכשל עם exit 1 |
| `preview.py` | בונה את דף ההשוואה מ-`directions.json` |
| `directions.json` · `preview.html` | תוצרים — לא לערוך ידנית |

**הכיוונים:** א׳ גשר (H227) · ב׳ עוגן TACT (steel-blue) · ג׳ ניגוד (אינדיגו+כתום) · ד׳ דואט (ציאן + שני צבעי האפליקציות).

אחרי הבחירה: נמחק את השלושה שלא נבחרו מ-`palette.py`, והנבחר יתקמפל
ל-`tokens.css` לאתר. הצבעים אף פעם לא מוקלדים ידנית ביעד.
