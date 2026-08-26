import { brand, footer, nav } from "../content/copy";
import { Logo } from "./Logo";

/** `sections` is off on the landing page, whose anchors do not exist there --
 *  a footer link that scrolls nowhere is worse than no link. */
export function Footer({ sections = true }: { sections?: boolean } = {}) {
  const year = new Date().getFullYear();
  return (
    <footer className="foot">
      <div className="container foot-inner">
        <div className="foot-brand">
          <Logo tone="reverse" size={38} />
          <span className="foot-tag">{footer.tagline}</span>
        </div>

        <nav className="foot-nav" aria-label="תחתון">
          {sections &&
            nav.map((n) => (
              <a key={n.id} href={`#${n.id}`}>
                {n.label}
              </a>
            ))}
          <a href={brand.appUrl}>{footer.appLink}</a>
          <a href="/privacy.html">{footer.privacy}</a>
        </nav>

        <p className="foot-legal">
          <span className="num">{year}</span> · {brand.group} · {footer.rights}
        </p>
      </div>
    </footer>
  );
}
