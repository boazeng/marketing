# המושבה ב׳ טבריה — תוכנית עבודה

זכויות ליחידות דיור בשכונת המושבה ב׳, רכס פוריה (תב״ע 207-0703876).
מחיר פתיחה מ־280,000 ₪ לפני מע״מ.

## מקור האמת — SharePoint
כל המסמכים של הפרויקט נקראים ונשמרים ישירות ב-SharePoint, לא מועתקים לריפו
(ראו DECISIONS.md):

https://yaelisrael.sharepoint.com/Shared Documents/TACT/שיווק/מכירת קרקע בטבריה/

| תיקייה | מה יש בה |
|---|---|
| מסמכים | `marketing-strategy.md` · `target-audience.md` (קהל יעד, 2026-10-01) |
| מיתוג | `brand-guide.md` |
| אתר | `landing-page-draft.md` · `moshava-b-site/index.html` |
| רשתות | `facebook-page-copy.md` · `facebook-posts-5.md` · `facebook-ads-text-only-approved.md` |

## וואטסאפ ללידים — 054-696-1875 (לשעבר "בוט אריאל")
מספר משותף לכל הקמפיינים, תחת העסק Urban Group. מפתחות: `WHATSAPP_*_ARIEL` ב-`.env`.

| שלב | סטטוס |
|---|---|
| שם תצוגה `Urban Group Marketing` | ⏳ הוגש ב-API ב-2026-09-27 · `PENDING_REVIEW` (השם הקודם "bot ariel" נדחה). נתקע עד הרישום |
| רישום ל-Cloud API | ✅ 2026-10-01 · `CONNECTED`, איכות GREEN · PIN ב-`WHATSAPP_2FA_PIN_ARIEL` |
| פרופיל (about, תיאור, מייל) | ✅ 2026-10-01 — Urban Group Marketing, `tactnmark@gmail.com` |
| webhook + בוט ניתוב לפי קמפיין | ⬜ WABA `1410564280615182` (עסק Urban Whatsup, מאומת) · אפליקציה `ariel` (915959480947721) מנויה. בוט אריאל של `urbangroup` **לא נדרש עוד** (בועז, 2026-10-01) — הבוט החדש מחליף אותו. אין App Secret ב-`.env` |
| חיבור באתר | ✅ `site/js/config.js` — ⚠️ האתר כבר באוויר; הכפתור לא יגיע לאף אחד עד שהרישום וה-webhook עובדים. לא לפרסם את הקישור לפני כן |

## אתר — https://moshava-b.newavera.co.il
**דף נחיתה** (מ-2026-10-05) — מחליף את האתר המלא. Mac mini · nginx סטטי · פורט 8108 ·
מנהרת Cloudflare ייעודית `moshava-b` (`8075b3d1-…`).

```
cd "המושבה ב טבריה/ops"
python deploy.py publish     # תמונות מ-SharePoint (-> WebP) -> העלאה -> בדיקה מקומית
python deploy.py verify      # בדיקה מבחוץ
```

| | |
|---|---|
| מקור העיצוב | SharePoint `אתר/moshava-b-landing/` (חוברת מאושרת 5.10.2026). **הקוד בריפו הוא הגרסה החיה** — תיקונים נעשים כאן, לא שם |
| מסר | רכישה משותפת · **₪280,000 + מע״מ** (₪330,400 כולל) לרכיב הקרקע · תקציב כולל ~1.46M |
| טופס | → `yazam-il.com/api/lead` (פרוקסי משותף) → TACT Task + טלגרם · `project: moshava-b` |
| פיקסל | `moshava-b` — PageView · Lead · Contact |
| תמונות | `site/assets/` נמשכות מ-SharePoint ומומרות ל-WebP (1.75MB → ~0.5MB). לא בגיט |
| פרטיות | `site/privacy.html` — ⬜ לאישור עו״ד |
| האתר הקודם | `site-v1/` (8 מדורים, מסר "זכות ליחידת דיור") — לא בשימוש |

## פייסבוק — https://www.facebook.com/1340214009171909
דף "טבריה - המושבה ב" · פורטפוליו **TACT NIRIM** · System User `yazamil publisher`
(טוקן `META_PAGE_TOKEN_BEDEK` — אותו משתמש משרת גם את בדק; טוקן הדף נגזר מ-`me/accounts`).

| | מצב (2026-10-01) |
|---|---|
| קטגוריה, about, קאבר, תמונת פרופיל | ✅ |
| אתר + מייל | ✅ הוגדרו ב-API |
| פוסטים | ⬜ אין — רק עדכוני קאבר/פרופיל מ-12.9 |
| עוקבים | 0 |
| אינסטגרם מקושר | ⬜ |
| כפתור וואטסאפ בדף | ⬜ |
| הרשאות מודעות לטוקן | ✅ 2026-10-03 — use case של Marketing API נוסף ל-`TACT Marketing`; `META_PAGE_TOKEN_BEDEK` הונפק מחדש עם `ads_management` · `ads_read` · `pages_manage_ads` |
| חשבון מודעות | `המושבה ב - טבריה` · `act_1501272988689802` · פעיל, **ILS · `Asia/Jerusalem`**, 0 הוצאה, בלי קמפיינים, בלי פיקסל ובלי אמצעי תשלום. נפתח בטעות ב-USD / `America/Los_Angeles` ותוקן במקום ב-2026-10-03: `POST act_…` עם `currency=ILS&timezone_id=70` עובד **כל עוד אין הוצאה**. חשבון שני נחסם — לפורטפוליו לא מאומת יש מכסה של חשבון מודעות אחד עד התשלום הראשון (שגיאה 3979) |
| אמצעי תשלום | ✅ PayPal, 2026-10-03 · תקציב יומי מינימלי ₪3.05 |
| בדיקת מוכנות (`validate_only`, לא נוצר כלום) | ✅ יצירת קמפיין · ✅ מודעה מפוסט קיים · ✅ מודעה עם תוכן חדש. האחרונה נכשלה כל עוד `TACT Marketing` הייתה ב-Development (`Ads creative post was created by an app that is in development mode`, subcode 1885183) ועברה אחרי **Publish** ב-2026-10-03 — בלי App Review ובלי טוקן חדש |
| פיקסל | ⬜ אין על חשבון המודעות ואין באתר. בלעדיו: רק תנועה / טופס לידים / וואטסאפ, בלי מדידת המרות |

TACT NIRIM · Business ID `1377755173854876`.

## מודעות מטא
חשבון מודעות **"TACT NIRIM"** `act_1501272988689802` (היחיד בפורטפוליו — משותף עם
קמפיין ייפוי הכוח של זהר; מטא מאפשרת כרגע חשבון אחד). תשלום: PayPal. טוקן:
`META_PAGE_TOKEN_BEDEK` (Tact publisher — כולל `ads_management`).

| | מצב (2026-10-05) |
|---|---|
| פיקסל `moshava-b` `28613934514923512` | ✅ מותקן באתר (`config.js` → `metaPixelId`). אירועים: `PageView`, `Lead` (טופס נשלח), `Contact` (לחיצת וואטסאפ) |
| בדיקת הפיקסל | ✅ PageView + Contact נצפו ברשת. ⚠️ fbevents **לא יורה בדפדפן אוטומטי** (`navigator.webdriver`) — בדיקת Playwright רגילה מחזירה אפס אירועים ונראית כמו תקלה. `Lead` לא נבדק כדי לא ליצור ליד מזויף |
| קמפיין | ⬜ |

## סטטוס
| שלב | סטטוס |
|---|---|
| 0 החלטות | — |
| 1 זהות | — |
| 2 דומיין | ✅ `moshava-b.newavera.co.il` (CNAME נוצר ע״י `cloudflared tunnel route dns`) |
| 3 אתר | ✅ באוויר 2026-09-27 · ✅ טופס לידים → פרוקסי הלידים המשותף ([bedek/ops/leads.md](../bedek/ops/leads.md)) → task-manager (tact ← לידים משיווק ← לידים) + טלגרם, 2026-10-04 · ⬜ ניסוחים לבדיקה משפטית |
| 4 רשתות | — |
| 5 מכירות | — |
| 6 תוכן | — |
