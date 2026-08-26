import { brand } from "../content/copy";

/**
 * The mark and the lockup.
 *
 * The path data is copied verbatim from `brand/logo/kit.py` -- that script is
 * the geometry's owner. Two things about it are load-bearing and must not be
 * "tidied": the arc caps stop exactly where the bead begins (no daylight), and
 * the break sits at 305 degrees rather than at twelve o'clock. Put it on the
 * vertical axis and the whole mark reads as a power button.
 */

type Tone = "brand" | "reverse";

const RING: Record<Tone, string> = {
  brand: "var(--brand)",
  reverse: "#FFFFFF",
};

export function Mark({ size = 40, tone = "brand" }: { size?: number; tone?: Tone }) {
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      aria-hidden="true"
      focusable="false"
    >
      <path
        d="M50.38 21.84 A21 21 0 1 1 35.26 11.25"
        fill="none"
        stroke={RING[tone]}
        strokeWidth={size <= 24 ? 8 : 7}
        strokeLinecap="round"
      />
      <circle cx="44.05" cy="14.8" r="6" fill="var(--accent)" />
    </svg>
  );
}

export function Logo({
  tone = "brand",
  size = 40,
  showGroup = true,
}: {
  tone?: Tone;
  size?: number;
  showGroup?: boolean;
}) {
  const ink = tone === "reverse" ? "#FFFFFF" : "var(--brand)";
  return (
    <span className="logo">
      <Mark size={size} tone={tone} />
      <span className="logo-text">
        {showGroup && (
          /* T·A·C·T is Latin and must stay LTR even mid-Hebrew. The raised
             dots are TACT's own device, recoloured from the group's rust to
             our amber. */
          <span className="logo-group ltr" style={{ color: ink }} aria-hidden="true">
            T<i>·</i>A<i>·</i>C<i>·</i>T
          </span>
        )}
        <span className="logo-word" style={{ color: ink }}>
          {brand.product}
        </span>
      </span>
      <span className="sr-only">
        {brand.group} {brand.product}
      </span>
    </span>
  );
}
