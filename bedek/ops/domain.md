# דומיין ו-DNS — yazam-il.com

**דומיין:** `yazam-il.com` · נרכש 2026-08-25 ב-domain the net.
**סטטוס:** ✅ נרכש · ⬜ ה-nameservers עדיין של הרשם (מצביע על עמוד חניה `62.219.91.45`)

---

## ההחלטה: Cloudflare ל-DNS, AWS לאחסון

**זה לא שני עולמות — זו בדיוק השיטה שלך היום.** בדקתי את החשבון:

| | |
|---|---|
| `newavera.co.il` | **Cloudflare** (`dom.ns.cloudflare.com` · `zoe.ns.cloudflare.com`) |
| Hosted zones ב-Route 53 | **אפס.** מעולם לא השתמשת בו |
| התפלגויות CloudFront בחשבון | **7** — ביניהן `tact-bedek`, `crm-db`, `sign`, `company-urban` |

כלומר כל אתר שלך כבר עובד כך: **Cloudflare עונה על "איפה האתר" → CloudFront
מגיש אותו מ-AWS.** הזמינות והעומס שדיברת עליהם מגיעים מ-CloudFront ומ-S3,
ואלה על AWS בדיוק כפי שביקשת. ה-DNS רק מפנה.

**Route 53** הוא שירות ה-DNS של אמזון — מקביל ל-Cloudflare, לא תוסף שלו.
להעביר אליו דומיין אחד היה יוצר דפוס נפרד מכל השאר, בתוספת 0.50$ לחודש,
בלי שום שיפור בזמינות. לכן — נשארים ב-Cloudflare.

---

## המצב הסופי

| רכיב | ערך |
|---|---|
| Zone ID | `afcf54981b9e77084dd1d7392566fa33` |
| שרתי שמות | `khalid.ns.cloudflare.com` · `lola.ns.cloudflare.com` |
| CNAME `@` + `www` | `d288tvmi7qlbjd.cloudfront.net` · **DNS only** |
| דלי S3 | `yazam-il-frontend-824980746386` (us-east-1, פרטי) |
| CloudFront | `E3G61PTI8DDHCV` |
| תעודה | ACM `00616ad1-…`, בתוקף עד 10.3.2027, **מתחדשת אוטומטית** |
| דואר | Email Routing — 3×MX + SPF + DKIM |

## ניהול DNS מכאן — `ops/cf.py`

הטוקן ב-`env\.env` כ-`CLOUDFLARE_API_TOKEN`, מוגבל ל-**Zone:DNS:Edit על
`yazam-il.com` בלבד**. הוא לא נוגע ב-`newavera.co.il`.

```bash
python cf.py list
python cf.py ensure CNAME app d288tvmi7qlbjd.cloudfront.net false
python cf.py ensure TXT  @   "<ערך האימות של מטא>"          false
```

⚠️ **תמיד `false` לפרוקסי** ברשומות שמצביעות ל-CloudFront. ענן כתום מוסיף
CDN שני מעל CDN, ופינוי מטמון ב-AWS מפסיק להשפיע על מה שהגולש רואה.

⚠️ **ל-`env\.env` אין שורה חדשה בסוף** — `grep '^KEY=...'` מפספס את השורה
האחרונה. `cf.py` מנתח את הקובץ במקום להתאים שורה.

## תת-דומיינים שנותרו
| כתובת | ל | סטטוס |
|---|---|---|
| `app.yazam-il.com` | הפניה ל-`tact-bedek.newavera.co.il` | ⬜ |
| `go.yazam-il.com` | קישורי מעקב לקמפיינים | ⬜ |
| TXT אימות מטא | לפני פתיחת פייסבוק/אינסטגרם | ⬜ |
