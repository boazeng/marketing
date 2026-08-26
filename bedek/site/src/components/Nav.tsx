import { useEffect, useState } from "react";
import { brand, cta, footer, nav } from "../content/copy";
import { Logo } from "./Logo";
import { Button } from "./Button";
import { Icon } from "./Icon";

export function Nav() {
  const [open, setOpen] = useState(false);
  const [lifted, setLifted] = useState(false);

  useEffect(() => {
    const onScroll = () => setLifted(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Escape closes the menu; a menu you can only close by aiming at a small
  // button is a menu people get stuck in.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <header className={`bar${lifted ? " bar--lifted" : ""}`}>
      <div className="container bar-inner">
        <a className="bar-logo" href="#top" aria-label={`${brand.group} ${brand.product}`}>
          <Logo size={34} />
        </a>

        <nav className={`bar-nav${open ? " is-open" : ""}`} aria-label="ראשי">
          {nav.map((n) => (
            <a key={n.id} href={`#${n.id}`} onClick={() => setOpen(false)}>
              {n.label}
            </a>
          ))}
          <a className="bar-nav-app" href={brand.appUrl}>
            {footer.appLink}
          </a>
        </nav>

        <div className="bar-actions">
          <Button href="#contact" variant="primary">
            {cta.primary}
          </Button>
          <button
            className="bar-toggle"
            aria-expanded={open}
            aria-label={open ? "סגירת התפריט" : "פתיחת התפריט"}
            onClick={() => setOpen((o) => !o)}
          >
            <Icon name={open ? "chevron" : "arrow"} size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}
