import { useId, useRef, useState } from "react";
import { brand, contact } from "../content/copy";
import { Button } from "./Button";
import { isEmail, isPhone, readCampaign, sendLead, type Lead } from "../lib/leads";
import { trackLead } from "../lib/pixel";

type Field = "name" | "company" | "phone" | "email" | "projects" | "note";
type Errors = Partial<Record<Field, string>>;

const EMPTY = {
  name: "",
  company: "",
  phone: "",
  email: "",
  projects: "",
  note: "",
};

export function LeadForm({ source }: { source: Lead["source"] }) {
  const uid = useId();
  const [v, setV] = useState(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [state, setState] = useState<"idle" | "sending" | "done" | "failed">("idle");
  // Captured once, on first render -- not on submit.
  const startedAt = useRef(Date.now());
  const honeypot = useRef<HTMLInputElement>(null);

  const set = (f: Field) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setV((prev) => ({ ...prev, [f]: e.target.value }));
    // clear the error as soon as the person starts fixing it, not on blur --
    // an error that lingers while you type reads as "still wrong"
    setErrors((prev) => (prev[f] ? { ...prev, [f]: undefined } : prev));
  };

  function validate(): Errors {
    const e: Errors = {};
    if (!v.name.trim()) e.name = contact.form.required;
    if (!v.company.trim()) e.company = contact.form.required;
    if (!v.phone.trim()) e.phone = contact.form.required;
    else if (!isPhone(v.phone)) e.phone = contact.form.badPhone;
    if (!v.email.trim()) e.email = contact.form.required;
    else if (!isEmail(v.email)) e.email = contact.form.badEmail;
    return e;
  }

  async function submit(ev: React.FormEvent) {
    ev.preventDefault();
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length) {
      document.getElementById(`${uid}-${Object.keys(e)[0]}`)?.focus();
      return;
    }
    setState("sending");
    try {
      await sendLead({
        ...v,
        source,
        campaign: readCampaign(),
        website: honeypot.current?.value ?? "",
        startedAt: startedAt.current,
      });
      // Only here: the proxy accepted it. Firing on click would count every
      // abandoned form as a lead and poison the ad optimisation.
      trackLead(source);
      setState("done");
    } catch {
      setState("failed");
    }
  }

  if (state === "done") {
    return (
      <p className="form-done" role="status">
        {contact.form.done}
      </p>
    );
  }

  const field = (f: Field, label: string, type = "text", wide = false) => (
    <div className={`field${wide ? " field--wide" : ""}`}>
      <label htmlFor={`${uid}-${f}`}>{label}</label>
      <input
        id={`${uid}-${f}`}
        name={f}
        type={type}
        value={v[f]}
        onChange={set(f)}
        dir={type === "email" || type === "tel" ? "ltr" : undefined}
        aria-invalid={errors[f] ? true : undefined}
        aria-describedby={errors[f] ? `${uid}-${f}-err` : undefined}
        autoComplete={
          { name: "name", company: "organization", phone: "tel", email: "email" }[
            f as string
          ] ?? "off"
        }
      />
      {errors[f] && (
        <span className="field-err" id={`${uid}-${f}-err`}>
          {errors[f]}
        </span>
      )}
    </div>
  );

  return (
    <form className="lead-form" onSubmit={submit} noValidate>
      {/* Honeypot. Not `display:none` -- some bots skip hidden inputs, and some
          screen readers announce them; this is off-screen, unfocusable and
          hidden from the accessibility tree instead. */}
      <div className="hp" aria-hidden="true">
        <label htmlFor={`${uid}-website`}>אל תמלא שדה זה</label>
        <input
          id={`${uid}-website`}
          ref={honeypot}
          type="text"
          name="website"
          tabIndex={-1}
          autoComplete="off"
          defaultValue=""
        />
      </div>

      <div className="lead-grid">
        {field("name", contact.form.name)}
        {field("company", contact.form.company)}
        {field("phone", contact.form.phone, "tel")}
        {field("email", contact.form.email, "email")}
        {field("projects", contact.form.projects)}
        <div className="field field--wide">
          <label htmlFor={`${uid}-note`}>{contact.form.note}</label>
          <textarea id={`${uid}-note`} name="note" rows={3} value={v.note} onChange={set("note")} />
        </div>
      </div>

      <Button as="button" type="submit" variant="primary" disabled={state === "sending"} full>
        {state === "sending" ? contact.form.sending : contact.form.submit}
      </Button>

      {state === "failed" && (
        <p className="form-error" role="alert">
          {contact.form.failed}
          <a className="ltr" href={`mailto:${brand.email}`}>
            {brand.email}
          </a>
        </p>
      )}
    </form>
  );
}
