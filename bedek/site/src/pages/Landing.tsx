import { brand, cta, hero, how, problem } from "../content/copy";
import { Logo } from "../components/Logo";
import { Button } from "../components/Button";
import { Icon, type IconName } from "../components/Icon";
import { LandingCta } from "../sections/Body";
import { Footer } from "../components/Footer";
import { Consent } from "../components/Consent";

/**
 * The paid-traffic page.
 *
 * Deliberately not the site with a shorter menu. Someone arriving from an ad
 * has one question and no patience: there is no nav to leave through, one
 * offer, and the form sits above the fold on desktop. Everything that exists
 * to help a browsing visitor -- features grid, FAQ, app matrix -- is cut,
 * because on this page it is somewhere else to go instead of converting.
 */
export default function Landing() {
  return (
    <>
      <a className="skip" href="#main">
        דילוג לתוכן
      </a>

      <header className="lp-bar" id="top">
        <div className="container lp-bar-inner">
          <Logo size={34} />
          {/* no navigation on purpose -- the only way off this page is the form */}
          <span className="lp-bar-note">{hero.eyebrow}</span>
        </div>
      </header>

      <main id="main">
        <section className="lp-hero">
          <div className="container lp-hero-inner">
            <div className="stack lp-hero-copy">
              <h1 className="hero-title">
                {hero.title[0]}
                <br />
                <span className="hero-title-2">{hero.title[1]}</span>
              </h1>
              <p className="lead">{hero.sub}</p>

              <ul className="lp-points">
                {how.steps.map((s) => (
                  <li key={s.k}>
                    <span className="lp-point-icon">
                      <Icon name={s.k as IconName} size={20} />
                    </span>
                    <span>
                      <b>{s.title}</b>
                      {s.body}
                    </span>
                  </li>
                ))}
              </ul>

              <Button href="#contact" variant="primary">
                {cta.primary}
              </Button>
            </div>

            <div className="lp-pain">
              <h2>{problem.title}</h2>
              <ul>
                {problem.items.map((p) => (
                  <li key={p.title}>
                    <Icon name="alert" size={18} />
                    <span>
                      <b>{p.title}</b>
                      {p.body}
                    </span>
                  </li>
                ))}
              </ul>
              <a className="lp-app-link" href={brand.appUrl}>
                כבר לקוח? כניסה למערכת
              </a>
            </div>
          </div>
        </section>

        <LandingCta />
      </main>

      <Footer sections={false} />
      <Consent />
    </>
  );
}
