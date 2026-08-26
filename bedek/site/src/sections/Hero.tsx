import { cta, hero } from "../content/copy";
import { Button } from "../components/Button";
import { Icon } from "../components/Icon";

/**
 * The hero opens on the thing a service manager actually wants: a single
 * screen that answers "how many are open and how many are late". The stat row
 * is the product's thesis, not decoration -- so it carries real numbers with
 * the late count marked, rather than three neutral figures.
 */
export function Hero() {
  return (
    <section className="hero" id="top">
      <div className="container hero-inner">
        <div className="hero-copy stack">
          <span className="eyebrow label">{hero.eyebrow}</span>
          <h1 className="hero-title">
            {hero.title[0]}
            <br />
            <span className="hero-title-2">{hero.title[1]}</span>
          </h1>
          <p className="lead hero-sub">{hero.sub}</p>
          <div className="hero-btns">
            <Button href="#contact" variant="primary">
              {cta.primary}
            </Button>
            <Button href="#how" variant="ghost">
              {cta.secondary}
            </Button>
          </div>
        </div>

        <div className="hero-panel" aria-hidden="true">
          <div className="panel-bar">
            <span className="panel-dot" />
            <span className="panel-title">כל הפרויקטים</span>
          </div>
          <div className="panel-stats">
            {hero.stats.map((s, i) => (
              <div className={`panel-stat${i === 2 ? " is-late" : ""}`} key={s.label}>
                <b className="num">{s.n}</b>
                <span>{s.label}</span>
              </div>
            ))}
          </div>
          <ul className="panel-rows">
            {[
              { loc: "בניין א׳ · קומה 3 · דירה 12", who: "אינסטלציה", late: false },
              { loc: "בניין ב׳ · קומה 1 · דירה 4", who: "חשמל", late: true },
              { loc: "בניין א׳ · קומה 7 · דירה 28", who: "אלומיניום", late: false },
            ].map((r) => (
              <li key={r.loc}>
                <Icon name={r.late ? "alert" : "check"} size={17} />
                <span className="panel-loc">{r.loc}</span>
                <span className="panel-who">{r.who}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
