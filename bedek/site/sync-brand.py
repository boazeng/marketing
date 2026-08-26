# -*- coding: utf-8 -*-
"""
Pulls the brand into the site. Run after any change under `brand/`.

The site never owns a colour, a font stack or a logo path -- it imports what
`brand/` generates. That is the whole reason the palette and the mark are
scripts and not files someone edits by hand.

    python sync-brand.py
"""
import io, os, shutil, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
BANNER = "/* SYNCED from {} by site/sync-brand.py -- do not edit here. */\n"


def run(script, cwd):
    subprocess.run([sys.executable, script], cwd=cwd, check=True,
                   stdout=subprocess.DEVNULL)


# regenerate first, so a stale tokens.css can never be copied forward
run("palette.py", os.path.join(ROOT, "brand", "palette"))
run("contrast.py", os.path.join(ROOT, "brand", "palette"))  # exits 1 on failure
run("kit.py", os.path.join(ROOT, "brand", "logo"))

pairs = [
    (("brand", "palette", "tokens.css"), ("src", "styles", "tokens.css")),
    (("brand", "fonts", "type.css"), ("src", "styles", "type.css")),
]
for src, dst in pairs:
    s, d = os.path.join(ROOT, *src), os.path.join(HERE, *dst)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    body = io.open(s, encoding="utf-8").read()
    io.open(d, "w", encoding="utf-8").write(BANNER.format("/".join(src)) + body)
    print("  ", "/".join(dst))

# the 404 page is generated, not hand-written, so it re-skins with the palette
subprocess.run([sys.executable, "make-404.py"], cwd=HERE, check=True)
subprocess.run([sys.executable, "make-privacy.py"], cwd=HERE, check=True)

logos = os.path.join(ROOT, "assets", "logos")
os.makedirs(os.path.join(HERE, "public"), exist_ok=True)
for name in ("mark.svg", "mark-reverse.svg", "favicon.svg", "app-icon.svg"):
    shutil.copy2(os.path.join(logos, name), os.path.join(HERE, "public", name))
    print("   public/" + name)

print("\nbrand synced.")
