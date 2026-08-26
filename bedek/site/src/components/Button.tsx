import type { ReactNode } from "react";

type Variant = "primary" | "ghost" | "quiet";

/**
 * A control says what happens when you press it. There is no "submit" or
 * "click here" anywhere on this site.
 */
export function Button({
  as = "a",
  href,
  variant = "primary",
  children,
  onClick,
  type,
  disabled,
  full,
}: {
  as?: "a" | "button";
  href?: string;
  variant?: Variant;
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
  full?: boolean;
}) {
  const className = `btn btn--${variant}${full ? " btn--full" : ""}`;
  if (as === "button") {
    return (
      <button className={className} onClick={onClick} type={type ?? "button"} disabled={disabled}>
        {children}
      </button>
    );
  }
  return (
    <a className={className} href={href} onClick={onClick}>
      {children}
    </a>
  );
}
