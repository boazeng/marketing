/**
 * Meta Pixel, loaded only after the visitor consents.
 *
 * The pixel is a tracker. Loading it before someone agrees would be a GDPR
 * violation for any EU visitor and, more practically, the kind of thing a
 * careful buyer notices. So nothing here runs on page load: `init()` is called
 * by the consent banner, and only if the answer was yes.
 *
 * The consent choice is stored in localStorage rather than a cookie, because a
 * cookie set to record a cookie preference is its own small joke.
 */

const PIXEL_ID = "1103415295693130";
const KEY = "yz-consent";

type Consent = "granted" | "denied";

declare global {
  interface Window {
    fbq?: ((...args: unknown[]) => void) & { callMethod?: (...a: unknown[]) => void; queue?: unknown[] };
    _fbq?: unknown;
  }
}

export function storedConsent(): Consent | null {
  try {
    const v = localStorage.getItem(KEY);
    return v === "granted" || v === "denied" ? v : null;
  } catch {
    // Safari in private mode throws on localStorage. Treat it as "not asked"
    // rather than crashing the page over an analytics preference.
    return null;
  }
}

export function storeConsent(v: Consent) {
  try {
    localStorage.setItem(KEY, v);
  } catch {
    /* nothing to do -- the banner simply reappears next visit */
  }
}

let loaded = false;

/** Injects the pixel and fires PageView. Safe to call more than once. */
export function init() {
  if (loaded || typeof window === "undefined") return;
  loaded = true;

  /* eslint-disable */
  (function (f: any, b: Document, e: string, v: string) {
    if (f.fbq) return;
    const n: any = (f.fbq = function () {
      n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
    });
    if (!f._fbq) f._fbq = n;
    n.push = n;
    n.loaded = true;
    n.version = "2.0";
    n.queue = [];
    const t = b.createElement(e) as HTMLScriptElement;
    t.async = true;
    t.src = v;
    const s = b.getElementsByTagName(e)[0];
    s.parentNode!.insertBefore(t, s);
  })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
  /* eslint-enable */

  window.fbq!("init", PIXEL_ID);
  window.fbq!("track", "PageView");
}

/**
 * A completed demo request. This is THE event that matters -- it is what lets
 * you tell which ad produced a lead rather than which ad produced a click.
 */
export function trackLead(source: "site" | "landing") {
  window.fbq?.("track", "Lead", { content_category: source });
}
