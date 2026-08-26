# TACT — מערך שיווק

תיקייה אחת לכל מותג. `bedek/` הוא הראשון, והוא גם התבנית.

| | |
|---|---|
| **[CLAUDE.md](CLAUDE.md)** | **התחל כאן.** הנחיות מלאות לסוכן — דרישות, סדר הרצה, וכל המלכודות |
| [PLAYBOOK.md](PLAYBOOK.md) | איך משווקים מוצר TACT חדש מאפס |
| [bedek/](bedek/) | המותג הראשון — [PLAN](bedek/PLAN.md) · [DECISIONS](bedek/DECISIONS.md) |

## מה נמצא כאן ומה לא

```
git          מה שמייצר   סקריפטים, קוד, החלטות, טקסטים    ← הריפו הזה
SharePoint   מה שנוצר    וידאו, PDF, תמונות               TACT/שיווק/<מותג>/
S3/CloudFront מה שמוגש   רק מה שצריך URL ציבורי
```

**אין כאן וידאו, PDF, תמונות שנוצרו בסקריפט או `node_modules`.** הכל נבנה
מחדש בפקודה. אין כאן גם אף סוד — המפתחות ב-`.env` משותף מחוץ לריפו.

## התחלה מהירה

```bash
pip install playwright pillow numpy && playwright install chromium
export TACT_ENV=/path/to/shared/.env      # אם לא בנתיב ברירת המחדל
cd bedek/site && npm install && python sync-brand.py && npm run dev
```

הרצף המלא ותנאי המערכת — ב-[CLAUDE.md](CLAUDE.md).

## בדק — מה חי

| | |
|---|---|
| אתר ודף נחיתה | https://yazam-il.com |
| סרטונים | `/video/{sheket,shlita}-{16x9,1x1,9x16}.mp4` |
| דף פייסבוק | `TACT בדק` — דומיין מאומת, פיקסל פעיל |
| לידים | טופס → CloudFront → HTTP API → Lambda → TACT-CRM + טלגרם |
