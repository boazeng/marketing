# -*- coding: utf-8 -*-
"""
WCAG AA gate for every palette direction. Exits 1 on any failure.

A palette generated from a spec needs a generated check -- a one-off manual
eyeball becomes a defect that every later direction inherits.

    python contrast.py
"""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")

# Paths resolve against this file, never the caller's cwd.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # Hebrew dies on cp1252 otherwise
from oklch import contrast_ratio

AA_TEXT, AA_LARGE, AA_UI = 4.5, 3.0, 3.0

# (foreground, background, minimum, what it is)
PAIRS = [
    ("inkStrong", "canvas",  AA_TEXT,  "body text on page"),
    ("inkStrong", "surface", AA_TEXT,  "body text on card"),
    ("inkSoft",   "canvas",  AA_TEXT,  "secondary text on page"),
    ("inkSoft",   "surface", AA_TEXT,  "secondary text on card"),
    ("inkFaint",  "surface", AA_LARGE, "captions (large only)"),
    ("brand",     "canvas",  AA_TEXT,  "brand text / links on page"),
    ("brand",     "surface", AA_TEXT,  "brand text / links on card"),
    ("brandDeep", "surface", AA_TEXT,  "brand deep on card"),
    ("brandInk",  "brandSoft", AA_TEXT, "text inside a brand tint"),
    ("accentDeep","surface", AA_TEXT,  "accent text on card"),
    ("border",    "canvas",  1.2,      "hairline visible at all"),
    ("appUser",   "surface", AA_UI,    "user-app swatch"),
    ("appCustomer","surface",AA_UI,    "customer-app swatch"),
]
# white text sitting on a filled block
ON_FILL = [("brand", AA_TEXT, "white on primary button"),
           ("brandDeep", AA_TEXT, "white on primary button hover"),
           ("accent", AA_UI, "white on CTA button (large text)"),
           ("accentDeep", AA_TEXT, "white on CTA hover")]


def check(directions):
    failed = 0
    for d in directions:
        c, rows = d["colors"], []
        for fg, bg, need, what in PAIRS:
            r = contrast_ratio(c[fg], c[bg])
            rows.append((r >= need, f"{fg:11}/{bg:10} {r:5.2f} (>= {need}) {what}"))
        for key, need, what in ON_FILL:
            r = contrast_ratio("#FFFFFF", c[key])
            rows.append((r >= need, f"{'#FFF':11}/{key:10} {r:5.2f} (>= {need}) {what}"))
        bad = [t for ok, t in rows if not ok]
        failed += len(bad)
        print(f'\n=== {d["name"]} ({d["title"]}) ===')
        if bad:
            for t in bad:
                print("  FAIL  " + t)
        else:
            print(f"  PASS  all {len(rows)} pairs")
    return failed


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "directions.json")
    n = check(json.load(io.open(src, encoding="utf-8")))
    if n:
        print(f"\n{n} contrast failures -- fix the spec in palette.py.")
        sys.exit(1)
    print("\nAll directions pass WCAG AA.")
