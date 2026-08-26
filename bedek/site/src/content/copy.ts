/**
 * Every word on the site, in one file.
 *
 * The source of truth is `content/messaging.md` one level up; this is that
 * document compiled for the build. Nothing in a component may hard-code a
 * sentence -- when the messaging changes we edit the markdown, then here, and
 * the whole site follows.
 *
 * Two claims are deliberately absent and must stay absent:
 *   - anything of the form "complies with the Sale Law". That is a legal
 *     promise; we describe a capability instead.
 *   - any mention of Google Play. There is no Android build yet.
 */

export const brand = {
  group: "T·A·C·T",
  product: "בדק",
  domain: "yazam-il.com",
  appUrl: "https://tact-bedek.newavera.co.il",
  /** The one public address. Shown as the fallback when the form cannot send,
   *  and printed on the one-pager. Changing it here changes it everywhere. */
  email: "office@yazam-il.com",
} as const;

export const nav = [
  { id: "problem", label: "הבעיה" },
  { id: "how", label: "איך זה עובד" },
  { id: "features", label: "יכולות" },
  { id: "apps", label: "האפליקציות" },
  { id: "faq", label: "שאלות" },
] as const;

export const cta = {
  primary: "לתיאום הדגמה",
  secondary: "איך זה עובד",
} as const;

export const hero = {
  // The domain is named after the customer (yazam) and the product after the
  // category (bedek). The eyebrow is where those two are tied together, so a
  // visitor landing on yazam-il.com is never confused about what this is.
  eyebrow: "ליזמים וקבלני בנייה",
  title: ["כל תקופת הבדק.", "במקום אחד."],
  sub:
    "מערכת אחת שמנהלת את הליקויים בכל הפרויקטים שלך — " +
    "מהרגע שהדייר מדווח ועד שהתקלה נסגרת, מתועדת וחתומה.",
  stats: [
    { n: "4", label: "פרויקטים" },
    { n: "312", label: "תקלות פתוחות" },
    { n: "18", label: "באיחור" },
  ],
} as const;

export const problem = {
  title: "אקסל, שלוש קבוצות וואטסאפ ומחברת",
  lead:
    "חוק המכר מחייב את היזם לתעד ולתקן לאורך תקופת הבדק. " +
    "בפועל זה מנוהל באקסלים ובוואטסאפים. שלוש תוצאות:",
  items: [
    {
      title: "תקלות נופלות בין הכיסאות",
      body: "אף אחד לא יודע להגיד כמה פתוחות עכשיו ומי מהקבלנים בפיגור.",
    },
    {
      title: "אין תיעוד",
      body: "כשמגיעה טענה שנה אחרי המסירה, אין מה להראות.",
    },
    {
      title: "הדייר לא יודע מה קורה",
      body: "ולכן מתקשר שוב ושוב — וזה הזמן של מנהל השירות.",
    },
  ],
} as const;

export const how = {
  title: "שלושה דברים שקורים בלעדיך",
  lead: "זה לא עוד אקסל עם מסך יפה. העבודה נכנסת למערכת לבד.",
  // A real sequence, so numbering it carries information.
  steps: [
    {
      k: "resident",
      title: "הדייר מדווח בעצמו",
      body:
        "קישור או קוד QR לדירה. בלי הורדה, בלי סיסמה. " +
        "הפנייה נכנסת ישירות כתקלה שממתינה לאישור שלך.",
    },
    {
      k: "field",
      title: "המפקח סוגר מהשטח",
      body:
        "אפליקציה בטלפון: סטטוס, תמונות, יומן טיפול וחתימה על פרוטוקול. " +
        "בלי לחזור למשרד.",
    },
    {
      k: "ai",
      title: "דוח הבדק נקרא לבד",
      body:
        "מעלים את ה-PDF, וסוכן AI מכניס את הליקויים מסווגים " +
        "ומוכנים לאישור.",
    },
  ],
} as const;

export const features = {
  title: "מה עוד יש בפנים",
  items: [
    {
      k: "tree",
      title: "מבנה פרויקט הירארכי",
      body: "בניין ← כניסה ← קומה ← יחידת ממכר. לכל תקלה יש כתובת מדויקת.",
    },
    {
      k: "pro",
      title: "קישור אישי לבעל מקצוע",
      body: "רואה רק את התקלות שלו באותו פרויקט. בלי התחברות, קריאה בלבד.",
    },
    {
      k: "sign",
      title: "פרוטוקול מסירה חתום",
      body: "חתימה דיגיטלית של הדייר, נשמרת בתוך ה-PDF.",
    },
    {
      k: "report",
      title: "דוחות להדפסה",
      body: "מסוננים לפי פרויקט, סטטוס, בעל מקצוע ותאריך.",
    },
  ],
} as const;

export const apps = {
  title: "שלושה ממשקים, מערכת אחת",
  lead:
    "לכל מי שנוגע בתקלה יש מסך משלו, וכולם עובדים על אותם נתונים.",
  items: [
    {
      k: "web",
      who: "ליזם",
      title: "אפליקציית דפדפן",
      body: "כל הפרויקטים, ניהול מלא, דוחות והרשאות.",
      status: "זמין",
    },
    {
      k: "user",
      who: "לאיש החברה",
      title: "אפליקציה לאייפון",
      body: "סקירה, תקלות, פרוטוקולים ודוחות — מהשטח.",
      status: "זמין",
    },
    {
      k: "customer",
      who: "לדייר",
      title: "אפליקציה לאייפון",
      body: "התקלות של הדירה ודיווח תקלה חדשה.",
      status: "זמין",
    },
  ],
  // Stated plainly rather than buried. Promising Android before it exists is
  // the fastest way to lose a developer's trust in a demo call.
  androidNote:
    "האפליקציות לנייד עובדות כרגע על אייפון. " +
    "גרסת אנדרואיד בפיתוח — והדייר בכל מקרה לא חייב אפליקציה: " +
    "הקישור נפתח בדפדפן בכל מכשיר.",
  androidCta: "עדכנו אותי כשתצא גרסת אנדרואיד",
} as const;

export const faq = {
  title: "שאלות שנשאלות בכל שיחה",
  items: [
    {
      q: "יש לי אקסל, זה עובד",
      a: "האקסל לא אומר לך מי באיחור, ולא מתעד מה נאמר לדייר.",
    },
    {
      q: "הדיירים לא ישתמשו באפליקציה",
      a:
        "הם לא צריכים. קישור בוואטסאפ נפתח בדפדפן. " +
        "האפליקציה היא בונוס למי שרוצה.",
    },
    {
      q: "כמה זמן לוקחת ההטמעה",
      a: "פרויקט ראשון עולה לאוויר באותו יום.",
    },
    {
      q: "מה עם המידע שלי",
      a:
        "כל חברה רואה אך ורק את הנתונים שלה. " +
        "מסד הנתונים פרטי, מאוחסן ב-AWS פרנקפורט.",
    },
    {
      q: "אין לכם אנדרואיד",
      a:
        "נכון. האפליקציות לנייד עובדות על אייפון, וגרסת אנדרואיד בפיתוח. " +
        "הדייר עובד גם בלי אפליקציה, בדפדפן.",
    },
  ],
} as const;

export const contact = {
  title: "נראה לך את זה על פרויקט אמיתי",
  lead:
    "הדגמה של עשרים דקות, בלי מצגת. נעלה פרויקט אחד שלך למערכת " +
    "ותראה איך זה נראה.",
  form: {
    name: "שם מלא",
    company: "חברה",
    phone: "טלפון",
    email: "אימייל",
    projects: "כמה פרויקטים פעילים",
    note: "משהו שכדאי שנדע מראש",
    submit: "שלחו לי הצעת מועד",
    sending: "שולח…",
    done: "קיבלנו. נחזור אליך תוך יום עסקים אחד.",
    // Says what went wrong and what to do instead -- never a bare "error".
    failed:
      "השליחה לא עברה. נסו שוב, או כתבו לנו ישירות ל-",
    required: "שדה חובה",
    badEmail: "כתובת אימייל לא תקינה",
    badPhone: "מספר טלפון לא תקין",
  },
} as const;

export const consent = {
  title: "עוגיות",
  body:
    "אנחנו משתמשים בעוגיות כדי למדוד מאיפה הגיעו הפניות. " +
    "בלי זה האתר עובד בדיוק אותו דבר.",
  link: "מדיניות פרטיות",
  accept: "מאשר",
  deny: "לא, תודה",
} as const;

export const footer = {
  tagline: "יזמות טכנולוגית",
  rights: "כל הזכויות שמורות",
  appLink: "כניסה למערכת",
  privacy: "מדיניות פרטיות",
} as const;
