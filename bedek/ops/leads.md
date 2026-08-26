# לידים — הארכיטקטורה שנבנתה

**סטטוס:** ✅ חי ונבדק מקצה לקצה. ⬜ חסר רק `CRM_API_KEY`.

```
דפדפן ──POST /api/lead──▶ CloudFront ──+x-origin-token──▶ HTTP API ──▶ Lambda
   (אותו origin, בלי CORS)                                              │
                                          ┌────────────────────────────┴──┐
                                          ▼                               ▼
                                  TACT-CRM /api/v1/customers        התראת טלגרם
                                  (X-API-Key מ-SSM)                 (תמיד נשלחת)
```

## למה לא ישירות מהדפדפן ל-CRM
`CRM_API_KEY` במשתנה `VITE_*` נצרב ל-bundle וניתן לקריאה בידי כל מבקר.
הפרוקסי מחזיק את המפתח; כתובתו ציבורית בכוונה כי אין בה סוד.

## שלוש החלטות שבנויות לתוך הקוד
1. **ליד לא הולך לאיבוד.** ההתראה בטלגרם נשלחת גם כשהכתיבה ל-CRM נכשלת,
   והמבקר מקבל 200. רק אם **שניהם** נכשלו הוא מקבל 502 ורואה כתובת חלופית.
2. **שום דבר לא סומך על הדפדפן.** הוולידציה בצד הלקוח נועדה לתת שגיאה מהירה
   ואדיבה; היא לא בקרה. הכול נבדק שוב ב-Lambda.
3. **honeypot + חותמת זמן.** שדה מוסתר שרק בוט ממלא, ובדיקה שההגשה לא הגיעה
   תוך פחות מ-3 שניות מרינדור העמוד. שניהם מחזירים **200** לבוט, כדי שלא
   יחזור לחפש חולשה.

## שתי דרכים שנוסו ונכשלו — לא לחזור אליהן
1. **Function URL ציבורי** → 403 תמיד, לא משנה מה במדיניות המשאב.
   **ציבורי חסום ברמת החשבון.**
2. **Function URL מאחורי CloudFront OAC** → `InvalidSignatureException` על כל
   POST. חתימת ה-sigv4 של OAC מסוג `lambda` **לא מכסה את גוף הבקשה**. אין
   הגדרה שמשנה את זה.

   ⚠️ **הכשל הזה מוסווה לחלוטין:** מיפוי ה-403→`/404.html` שלנו הופך אותו
   ל-404 רגיל עם `Server: AmazonS3`, ו**אין שום דבר בלוגים של ה-Lambda**.
   כדי לראות סטטוס אמיתי צריך לכבות זמנית את `CustomErrorResponses`.

**מה שכן עובד:** CloudFront → HTTP API → Lambda. זה גם הדפוס של tact-crm.

## מלכודות קטנות שעלו בדרך
- **תבניות נתיב ב-CloudFront הן יחסיות.** `api/lead`, לא `/api/lead` — עם
  לוכסן מוביל התבנית לא מתאימה לכלום והבקשה נופלת ל-S3.
- **CloudFront שומר את הקידומת `X-Edge-*`** ודוחה אותה ב-`CustomHeaders`.
  הכותרת נקראת `x-origin-token`.
- **`UpdateDistribution` דורש את מלוא שדות ה-legacy** ומדווח על אחד חסר בכל
  סבב. הסקריפט מציין את כולם מראש.
- **`aws` ב-Windows הוא `aws.cmd`** — `subprocess` לא מוצא `aws` חשוף.

## הקבצים
| קובץ | תפקיד |
|---|---|
| `lead-proxy/handler.py` | הפונקציה. ספרייה תקנית בלבד + boto3 של ה-runtime |
| `lead-proxy/deploy.py` | תפקיד IAM, Lambda, סודות ב-SSM, בדיקה |
| `lead-proxy/attach-to-cdn.py` | HTTP API + חיבור ל-CloudFront ב-`/api/lead` |

```bash
python deploy.py deploy         # לעדכן את קוד הפונקציה
python deploy.py test           # ליד סינתטי דרך ה-CDN החי
python attach-to-cdn.py         # רק אם משנים את החיווט
```

## מה שנשאר
**מפתח API ב-TACT-CRM** (ניהול חברה → מפתחות API), ואז:
```bash
CRM_API_KEY=<המפתח> python deploy.py secrets
```
בלעדיו הליד מגיע לטלגרם אבל לא נכנס ל-CRM, וההודעה מסומנת 🔴.

**רשומות SSM:** `yazam-il-crm-api-key` · `yazam-il-telegram-token` ·
`yazam-il-telegram-chat` · `yazam-il-edge-secret`. תפקיד ה-Lambda קורא
בדיוק את הארבעה האלה ולא יותר.

⚠️ ההתראות הולכות כרגע ל-`RAN_TELEGRAM_CHAT_ID` מה-env המשותף. אם צריך
צ'אט ייעודי ללידים — לעדכן את `yazam-il-telegram-chat`.
