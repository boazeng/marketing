/**
 * הגדרות האתר — מלאו לפני העלאה לשרת
 * אם formEndpoint ריק, הטופס יפתח וואטסאפ עם הודעה מוכנה.
 */
window.SITE_CONFIG = {
  // מספר וואטסאפ בפורמט בינלאומי ללא + (למשל: 972501234567)
  // מספר הלידים המשותף "Urban Group Marketing" — Cloud API, הודעות מגיעות
  // ל-webhook ולא לאפליקציה בטלפון. ראו DECISIONS.md ו-PLAN.md.
  whatsappNumber: "972546961875",

  // כתובת API לשליחת הטופס (POST JSON). השאירו ריק לשימוש בוואטסאפ.
  // זה פרוקסי הלידים המשותף לכל אתרי TACT (bedek/ops/leads.md): הוא רושם
  // את הליד ב-TACT Task ושולח התראה בטלגרם. אין כאן סוד — הכתובת ציבורית.
  formEndpoint: "https://yazam-il.com/api/lead",

  // קישור לעמוד פייסבוק (אופציונלי)
  facebookUrl: "https://www.facebook.com/1340214009171909",

  // מספר טלפון להצגה באתר (למשל: 050-123-4567)
  phoneDisplay: "054-696-1875",

  // מייל ליצירת קשר להצגה באתר
  email: "tactnmark@gmail.com",

  // פיקסל מטא "moshava-b" (פורטפוליו TACT NIRIM). ריק = בלי מעקב.
  // מזהה פיקסל אינו סוד — הוא גלוי בכל דף שטוען אותו.
  metaPixelId: "28613934514923512"
};
