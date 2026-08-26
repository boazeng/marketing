import { useEffect, useState } from "react";
import { init, storeConsent, storedConsent } from "../lib/pixel";
import { consent as copy } from "../content/copy";

/**
 * Cookie consent.
 *
 * Two things it deliberately does NOT do, both of which are common and both of
 * which are dark patterns: it does not make "accept" visually louder than
 * "decline", and it does not treat continued scrolling as agreement. A visitor
 * who says no is simply not tracked, and is not asked again.
 *
 * It renders nothing at all once a choice exists, so a returning visitor never
 * sees it twice.
 */
export function Consent() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const prior = storedConsent();
    if (prior === "granted") init();
    else if (prior === null) setOpen(true);
  }, []);

  if (!open) return null;

  const decide = (v: "granted" | "denied") => {
    storeConsent(v);
    if (v === "granted") init();
    setOpen(false);
  };

  return (
    <div className="consent" role="dialog" aria-live="polite" aria-label={copy.title}>
      <p>
        {copy.body}{" "}
        <a href="/privacy.html">{copy.link}</a>
      </p>
      <div className="consent-actions">
        {/* Same weight on both buttons -- refusing must be as easy as agreeing. */}
        <button className="btn btn--ghost" onClick={() => decide("denied")}>
          {copy.deny}
        </button>
        <button className="btn btn--primary" onClick={() => decide("granted")}>
          {copy.accept}
        </button>
      </div>
    </div>
  );
}
