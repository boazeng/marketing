/**
 * One line-icon family: 24x24, currentColor, 1.7 stroke, round caps and joins.
 *
 * Every glyph is drawn on the same grid with the same weight so a row of them
 * reads as one set. Add new glyphs inside GLYPHS only -- an icon imported from
 * somewhere else will not match, and the mismatch is visible immediately.
 */

const GLYPHS = {
  // how it works
  resident: "M3 11 12 4l9 7M5 10v9h14v-9M10 19v-5h4v5",
  field: "M7 3h10a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1ZM11 18h2",
  ai: "M8 3h6l4 4v14H6V5a2 2 0 0 1 2-2ZM14 3v4h4M9 13h6M9 17h4",

  // features
  tree: "M12 3v4M12 11v4M6 21v-4M18 21v-4M6 17h12v-2M12 7v4M10 3h4v4h-4zM4 17h4v4H4zM16 17h4v4h-4z",
  pro: "M12 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8ZM4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1",
  sign: "M4 17c3-1 4-9 7-9s2 6 4 6 2-2 4-2M4 21h16",
  report: "M8 3h8l3 3v15H5V6l3-3ZM8 3v4H5M9 12h6M9 16h6",

  // apps
  web: "M3 6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM8 21h8M12 17v4",
  user: "M8 2h8a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1ZM11 19h2",
  customer: "M4 10 12 4l8 6v9a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM10 20v-6h4v6",

  // ui
  check: "M4 12.5 9 17.5 20 6.5",
  arrow: "M19 12H5M11 6l-6 6 6 6",
  chevron: "M15 6l-6 6 6 6",
  alert: "M12 3 2 20h20L12 3ZM12 10v5M12 17.5v.5",
  clock: "M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18ZM12 7v5l3.5 2",
} as const;

export type IconName = keyof typeof GLYPHS;

export function Icon({
  name,
  size = 24,
  className,
}: {
  name: IconName;
  size?: number;
  className?: string;
}) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      focusable="false"
    >
      <path d={GLYPHS[name]} />
    </svg>
  );
}
