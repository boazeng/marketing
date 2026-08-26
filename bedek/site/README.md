# האתר — TACT בדק

React 18 + Vite + TypeScript. שני עמודים, בלי ראוטר.

| עמוד | קובץ | למה |
|---|---|---|
| אתר התדמית | `index.html` → `src/main.tsx` | עמוד גלילה אחד עם עוגנים |
| דף נחיתה | `landing.html` → `src/landing-entry.tsx` | תנועה בתשלום. `noindex`, בלי ניווט |

## הרצה
```bash
npm install && npm run dev
```

## המותג לא נמצא כאן
כל צבע, פונט ולוגו מגיעים מ-`brand/` דרך סקריפט. אחרי כל שינוי שם:
```bash
python sync-brand.py
```
הוא מריץ מחדש את `palette.py`, את בדיקת הניגודיות (**נכשל עם exit 1**) ואת
`kit.py`, ואז מעתיק ל-`src/styles/` ול-`public/`. **אין לערוך את הקבצים
המסונכרנים** — הם נדרסים.

## הטקסטים לא נמצאים ברכיבים
כל מילה יושבת ב-`src/content/copy.ts`, שהוא הקומפילציה של
`content/messaging.md`. רכיב לא מכיל משפט.

שני דברים אסורים שם, וגם בכל טקסט עתידי:
- ❌ "עומד בחוק המכר" — הבטחה משפטית. במקום: "בנוי לתיעוד הנדרש בתקופת הבדק".
- ❌ כל אזכור של Google Play — אין אנדרואיד.

## לידים
הטופס שולח ל-`VITE_LEAD_ENDPOINT` — פרוקסי, לא ה-CRM ישירות.
**אסור לשים `CRM_API_KEY` במשתנה `VITE_`** — הוא נצרב ל-bundle ונחשף.
ההסבר המלא והחוזה: [`ops/leads.md`](../ops/leads.md).

## מלכודת שנתפסה כאן
שמות קבצים ב-Windows הם **case-insensitive**: `src/landing.tsx` ו-
`src/Landing.tsx` הם אותו קובץ. רכיב שנכתב ב-`Landing.tsx` דרס בשקט את נקודת
הכניסה, ה-build עבר בהצלחה, והעמוד עלה **ריק**. לכן נקודת הכניסה נקראת
`landing-entry.tsx` והרכיב יושב ב-`pages/`.

## מבנה
```
src/
  content/copy.ts       כל הטקסט
  lib/leads.ts          שליחת ליד + ולידציה
  styles/               base + components (tokens ו-type מסונכרנים)
  components/           Logo · Icon · Button · Nav · Footer · LeadForm
  sections/Body.tsx     סקשנים של עמוד הבית
  sections/Hero.tsx
  pages/Landing.tsx     דף הנחיתה
```
