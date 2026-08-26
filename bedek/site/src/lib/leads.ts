/**
 * Sending a lead.
 *
 * IMPORTANT -- the browser never holds the CRM key. Anything in a `VITE_`
 * variable is compiled into the bundle and readable by every visitor, so
 * posting straight to TACT-CRM with an API key from here would publish that
 * key. The form posts to a thin proxy we own instead; the proxy holds the key
 * and forwards to the CRM. `VITE_LEAD_ENDPOINT` is that proxy's URL, which is
 * public by design.
 *
 * See `ops/leads.md` for the proxy's contract and deployment.
 */

export type Lead = {
  name: string;
  company: string;
  phone: string;
  email: string;
  projects?: string;
  note?: string;
  /** which page produced it -- the site or a paid landing page */
  source: "site" | "landing";
  /** utm_* off the URL, so we can tell which campaign paid for this */
  campaign?: Record<string, string>;
  /** Honeypot. Hidden from people; bots fill every field they find. Must stay
   *  empty -- the proxy answers 200 and drops the lead when it is not. */
  website?: string;
  /** When the form first rendered. The proxy discards anything submitted
   *  within a few seconds of it, which no person can do. */
  startedAt?: number;
};

const ENDPOINT = import.meta.env.VITE_LEAD_ENDPOINT as string | undefined;

/** utm_source, utm_medium, utm_campaign, utm_content, utm_term, gclid, fbclid */
export function readCampaign(search = window.location.search): Record<string, string> {
  const out: Record<string, string> = {};
  const p = new URLSearchParams(search);
  for (const [k, v] of p.entries()) {
    if (k.startsWith("utm_") || k === "gclid" || k === "fbclid") out[k] = v;
  }
  return out;
}

export async function sendLead(lead: Lead): Promise<void> {
  if (!ENDPOINT) {
    // Not configured yet. Fail loudly in dev so a missing endpoint is caught
    // during development rather than silently eating a real lead in
    // production -- a lead that vanishes without an error is the worst
    // possible outcome here.
    if (import.meta.env.DEV) {
      console.warn("VITE_LEAD_ENDPOINT is not set; lead not sent:", lead);
      return;
    }
    throw new Error("lead endpoint not configured");
  }

  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...lead, at: new Date().toISOString() }),
  });

  if (!res.ok) throw new Error(`lead endpoint returned ${res.status}`);
}

/* ------------------------------------------------------------ validation */

export const isEmail = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim());

/** Israeli mobile or landline, with or without separators and +972. */
export const isPhone = (v: string) => {
  const d = v.replace(/[\s-()]/g, "").replace(/^\+972/, "0");
  return /^0(5\d|[2-4,8-9]|7\d)\d{7}$/.test(d);
};
