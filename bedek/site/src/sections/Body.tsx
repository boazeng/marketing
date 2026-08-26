import { apps, contact, faq, features, how, problem } from "../content/copy";
import { Icon, type IconName } from "../components/Icon";
import { LeadForm } from "../components/LeadForm";

export function Problem() {
  return (
    <section className="section section--tint" id="problem">
      <div className="container">
        <div className="section-head">
          <h2>{problem.title}</h2>
          <p className="lead">{problem.lead}</p>
        </div>
        <div className="grid grid--3">
          {problem.items.map((it) => (
            <article className="card card--plain" key={it.title}>
              <span className="card-alert">
                <Icon name="alert" size={20} />
              </span>
              <h3>{it.title}</h3>
              <p>{it.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export function How() {
  return (
    <section className="section" id="how">
      <div className="container">
        <div className="section-head">
          <h2>{how.title}</h2>
          <p className="lead">{how.lead}</p>
        </div>
        {/* Numbered because this genuinely is a sequence: the resident reports,
            the inspector closes, and the report is parsed on the way in. */}
        <ol className="steps">
          {how.steps.map((s, i) => (
            <li className="step" key={s.k}>
              <span className="step-num num">{i + 1}</span>
              <span className="step-icon">
                <Icon name={s.k as IconName} size={26} />
              </span>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

export function Features() {
  return (
    <section className="section section--tint" id="features">
      <div className="container">
        <div className="section-head">
          <h2>{features.title}</h2>
        </div>
        <div className="grid grid--4">
          {features.items.map((f) => (
            <article className="card" key={f.k}>
              <span className="card-icon">
                <Icon name={f.k as IconName} size={22} />
              </span>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Apps() {
  return (
    <section className="section" id="apps">
      <div className="container">
        <div className="section-head">
          <h2>{apps.title}</h2>
          <p className="lead">{apps.lead}</p>
        </div>
        <div className="grid grid--3">
          {apps.items.map((a) => (
            <article className="card card--app" key={a.k}>
              <span className="card-icon">
                <Icon name={a.k as IconName} size={22} />
              </span>
              <span className="card-who label">{a.who}</span>
              <h3>{a.title}</h3>
              <p>{a.body}</p>
              <span className="badge">{a.status}</span>
            </article>
          ))}
        </div>
        <aside className="note-android">
          <Icon name="clock" size={20} />
          <div>
            <p>{apps.androidNote}</p>
            <a href="#contact">{apps.androidCta}</a>
          </div>
        </aside>
      </div>
    </section>
  );
}

export function Faq() {
  return (
    <section className="section section--tint" id="faq">
      <div className="container">
        <div className="section-head">
          <h2>{faq.title}</h2>
        </div>
        <div className="faq">
          {faq.items.map((f) => (
            <details key={f.q}>
              <summary>
                <span>{f.q}</span>
                <Icon name="chevron" size={20} />
              </summary>
              <p>{f.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Contact() {
  return (
    <section className="section section--brand" id="contact">
      <div className="container contact-inner">
        <div className="contact-copy stack">
          <h2>{contact.title}</h2>
          <p className="lead">{contact.lead}</p>
          <ul className="contact-points">
            {["עשרים דקות", "על פרויקט אמיתי שלך", "בלי מצגת"].map((p) => (
              <li key={p}>
                <Icon name="check" size={18} />
                {p}
              </li>
            ))}
          </ul>
        </div>
        <div className="contact-card">
          <LeadForm source="site" />
        </div>
      </div>
    </section>
  );
}

export function LandingCta() {
  return (
    <section className="section section--brand" id="contact">
      <div className="container contact-inner">
        <div className="contact-copy stack">
          <h2>{contact.title}</h2>
          <p className="lead">{contact.lead}</p>
          <ul className="contact-points">
            {["עשרים דקות", "על פרויקט אמיתי שלך", "בלי מצגת"].map((p) => (
              <li key={p}>
                <Icon name="check" size={18} />
                {p}
              </li>
            ))}
          </ul>
        </div>
        <div className="contact-card">
          <LeadForm source="landing" />
        </div>
      </div>
    </section>
  );
}
