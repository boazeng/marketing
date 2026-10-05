/**
 * הגדרות דף הנחיתה. אין כאן סוד — כל ערך גלוי לכל מבקר.
 */
window.SITE_CONFIG = {
  // מספר הלידים המשותף "Urban Group Marketing" — WhatsApp Cloud API: הודעות
  // מגיעות ל-webhook ולא לאפליקציה בטלפון. ראו DECISIONS.md ו-PLAN.md.
  whatsappNumber: "972546961875",

  // פרוקסי הלידים המשותף לכל אתרי TACT (bedek/ops/leads.md): רושם את הליד
  // ב-TACT Task ושולח התראה בטלגרם. ריק = הטופס נפתח בוואטסאפ.
  formEndpoint: "https://yazam-il.com/api/lead",

  // פיקסל מטא "moshava-b" (פורטפוליו TACT NIRIM). ריק = בלי מעקב.
  metaPixelId: "28613934514923512"
};
