# מטא — הקמה לקראת קמפיין

**הכול בתוך הפורטפוליו Urban Group:** דף, חשבון מודעות, פיקסל, אפליקציה ו-System User.
הנימוק ב-[DECISIONS.md](../DECISIONS.md).
המלכודות הכלליות של מטא — ב-[bedek/social/meta-setup.md](../../bedek/social/meta-setup.md); לא חוזרים עליהן כאן.

**נדחה: שיתוף Partner ל-TACT NIRIM ושימוש בטוקן הקיים.** אפליקציה במצב Development
מספיקה רק לנכסים של אותו פורטפוליו; בשיתוף, הדף וחשבון המודעות שייכים לפורטפוליו
אחר מהאפליקציה. לא נוסה — ירדנו ממנו לפני.

## מזהי הנכסים (מתעדכן תוך כדי)

| נכס | ערך | סטטוס |
|---|---|---|
| Business Portfolio | **Urban Group** · ID **1478082143932396** (שונה 2026-10-03; `urban marketing` נדחה בגלל אות קטנה) | ✅ |
| System User | `Urban Publisher` · **61594730175940** (ב-API: `122106204291491005`) · Admin | ✅ משויך לדף, לאפליקציה ולחשבון המודעות |
| Facebook Page | `אחזקה אורבנית` · Page ID **1047533558446539** (המספר `61574389955730` שבקישור `profile.php` הוא מזהה פרופיל, לא Page ID). קטגוריה Local service · 0 עוקבים · בלי תמונת פרופיל · בלי פוסטים | ✅ בבעלות Urban Group |
| App | `Urban Automated Marketing` · **810701747992714** (לשעבר `vibe marketing`) · use cases: Marketing API + Manage everything on your Page · Unpublished | ✅ |
| App — לא לגעת | `urbanmarketing` · 1622361175662441 — בוט הוואטסאפ של האנרגיה רץ עליה | — |
| Ad account | `Urban ad account` · **act_1229610818877667** · ILS · `Asia/Jerusalem` · 0 הוצאה · בלי קמפיינים. קיים מ-2026-02-27; שויך ל-System User ב-API ב-2026-10-03 | ✅ |
| אמצעי תשלום | VISA *6213 | ✅ |
| Dataset / Pixel | — | ⬜ ליצור כשיש דומיין |
| טוקן | `META_TOKEN_URBAN_ADS` בכספת (`prod/meta`) · ללא תפוגה · `ads_management` `ads_read` `business_management` `pages_manage_ads` `pages_manage_posts` `pages_manage_metadata` `pages_manage_engagement` `pages_read_engagement` `pages_show_list` | ✅ אומת מול Graph API 2026-10-03 |
| אימות עסקי | `not_verified` | ⬜ לא חוסם דף, טוקן או מודעות |
| Instagram | — | ⬜ לא חוסם — מודעה רצה באינסטגרם גם בזהות הדף |

## הרצף

| # | שלב | איפה | מי |
|---|---|---|---|
| 1 | System User ↔ דף | System users → Assign assets → Pages | בועז |
| 2 | אפליקציה עם use cases: ניהול דף + Marketing API | developers.facebook.com, משויכת ל-Urban Group | בועז |
| 3 | System User ↔ אפליקציה | Assign assets → Apps | בועז |
| 4 | חשבון מודעות + שיוך ל-System User | Accounts → Ad accounts → Add → Create | בועז |
| 5 | אמצעי תשלום + פרטי חשבונית | חשבון המודעות → Billing & payments | בועז |
| 6 | Dataset, מקושר לחשבון המודעות ומשויך ל-System User | Data sources → Datasets → Add | בועז |
| 7 | טוקן | System User → Generate token → ל-`.env` | בועז |
| 8 | אימות בקריאה מ-Graph API, התקנת פיקסל, בניית קמפיין במצב `PAUSED` | | Claude |

⚠️ **אזור זמן ומטבע של חשבון מודעות נקבעים ביצירה ולא ניתנים לשינוי.**
`Asia/Jerusalem` + `ILS`. טעות כאן = חשבון חדש.

⚠️ **שמות באות גדולה.** מטא דחתה `urban marketing` לפורטפוליו; אותו כלל חל על דף.

⚠️ **לא ללחוץ Generate token לפני שהאפליקציה משויכת** — יוצא טוקן בלי הרשאות.

⚠️ **אפליקציה ב-Development לא יכולה ליצור מודעה עם תוכן חדש.** קמפיין נוצר, מודעה
מפוסט קיים נוצרת, אבל `object_story_spec` נדחה: `Ads creative post was created by an
app that is in development mode` (subcode 1885183). הפתרון: **Publish** לאפליקציה.
ב-`TACT Marketing` זה עבר ב-2026-10-03 בלי App Review ובלי טוקן חדש.
`Urban Automated Marketing` עדיין ב-Development — ⬜ לפרסם.

הרשאות לטוקן: `ads_management` · `ads_read` · `business_management` ·
`pages_manage_ads` · `pages_read_engagement` · `pages_show_list` ·
`pages_manage_posts` · `pages_manage_metadata` · `leads_retrieval`.
