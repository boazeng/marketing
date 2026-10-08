# -*- coding: utf-8 -*-
"""
Publishes this project's finished deliverables to SharePoint. Same rules and
same Graph client as bedek/ops/sharepoint.py -- read that one for the why.

    python sharepoint.py --plan      show what would be uploaded, change nothing
    python sharepoint.py             upload

The landing page is NOT here: it flows the other way, from SharePoint to the
server (deploy.py).
"""
import os, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.normpath(os.path.join(ROOT, "..", "bedek", "ops")))
from sharepoint import Graph, env, human  # noqa: E402

BASE = "TACT/שיווק/יפוי כח מתמשך"

# (local path relative to the project folder, destination subfolder)
# "חומרים לאישור" holds what the lawyer has not signed off yet; nothing in it
# may be published. "מודעות מאושרות" is the only folder the campaign draws on.
# Every ad in every placement size: 4 ads x 4 formats (social/ads.py, FORMATS).
APPROVED = "רשתות/מודעות מאושרות"
MANIFEST = [("social/out/ads-approved.pdf", APPROVED)] + [
    (f"social/out/ad-{n}-{fmt}.png", APPROVED)
    for n in range(1, 5) for fmt in ("1x1", "4x5", "9x16", "191x100")
]


if __name__ == "__main__":
    plan_only = "--plan" in sys.argv
    g = None if plan_only else Graph()

    missing, todo, same = [], [], 0
    for rel, sub in MANIFEST:
        local = os.path.join(ROOT, rel)
        if not os.path.exists(local):
            missing.append(rel)
            continue
        dest = f"{BASE}/{sub}/{os.path.basename(rel)}"
        size = os.path.getsize(local)
        if g and g.remote_size(dest) == size:
            same += 1
        else:
            todo.append((local, dest, size))

    for m in missing:
        print(f"חסר מקומית (דלג):  {m}")
    if same:
        print(f"כבר מעודכן: {same} קבצים")
    print(f"{'היה מועלה' if plan_only else 'יועלה'}: {len(todo)} קבצים, "
          f"{human(sum(s for _, _, s in todo))}")
    for _, dest, size in todo:
        print(f"   {dest}   {human(size)}")

    if plan_only or not todo:
        sys.exit(0)

    for f in sorted({os.path.dirname(d) for _, d, _ in todo}):
        g.ensure_folder(f)
    for local, dest, size in todo:
        g.upload(local, dest)
        # Read it back: an upload that returned without error is not yet a file.
        ok = g.remote_size(dest) == size
        print(f"   {'הועלה' if ok else '!! לא אומת'}  {dest}")
    print(f"\n-> {env('SHAREPOINT_SITE_URL')}")
