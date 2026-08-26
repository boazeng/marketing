# -*- coding: utf-8 -*-
"""
Publishes the finished deliverables to SharePoint, where the rest of the
organisation can actually see them.

The division of labour across the three stores:

    git          what PRODUCES  -- scripts, source, decisions
    SharePoint   what was MADE  -- video, PDF, images, documents
    S3/CloudFront what is SERVED -- only things needing a public URL

So this uploads outputs, never sources. A person opening the folder should
find things they can watch and read, not a checkout.

    python sharepoint.py --plan      show what would be uploaded, change nothing
    python sharepoint.py             upload

Idempotent: a file whose name and byte size already match on the far side is
skipped, so re-running after one new video costs one upload.
"""
import io, json, os, sys, urllib.error, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
# The shared secrets file. Override with TACT_ENV on a machine where it
# lives elsewhere -- nothing in this repo may ever contain a secret.
ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")

BRAND = "בדק"
BASE = f"TACT/שיווק/{BRAND}"

# (local path relative to the marketing folder, destination subfolder)
# Anything not listed here stays out -- that is the point.
MANIFEST = [
    ("video/out/sheket-16x9.mp4",        "סרטונים"),
    ("video/out/sheket-1x1.mp4",         "סרטונים"),
    ("video/out/sheket-9x16.mp4",        "סרטונים"),
    ("video/out/shlita-16x9.mp4",        "סרטונים"),
    ("video/out/shlita-1x1.mp4",         "סרטונים"),
    ("video/out/shlita-9x16.mp4",        "סרטונים"),
    ("content/onepager/onepager.pdf",    "חומר מכירה"),
    ("content/onepager/onepager.png",    "חומר מכירה"),
    ("assets/logos/mark.svg",            "מיתוג"),
    ("assets/logos/mark-reverse.svg",    "מיתוג"),
    ("assets/logos/mark-mono.svg",       "מיתוג"),
    ("assets/logos/app-icon.svg",        "מיתוג"),
    ("brand/palette/tokens.css",         "מיתוג"),
    ("brand/logo/logo-kit.html",         "מיתוג"),
    ("social/out/profile.png",           "רשתות"),
    ("social/out/cover.png",             "רשתות"),
    ("_pdf/PLAN.pdf",                    "מסמכים"),
    ("_pdf/DECISIONS.pdf",               "מסמכים"),
    ("_pdf/brand-brief.pdf",             "מסמכים"),
    ("_pdf/messaging.pdf",               "מסמכים"),
    ("_pdf/meta-setup.pdf",              "מסמכים"),
    ("_pdf/playbook.pdf",                "מסמכים"),
]

CHUNK = 5 * 1024 * 1024          # Graph requires a multiple of 320 KiB


def env(key):
    for raw in io.open(ENV, encoding="utf-8", errors="replace").read().splitlines():
        l = raw.strip().lstrip("\ufeff")
        if l.startswith(key + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{key} not in the shared .env")


def token():
    body = urllib.parse.urlencode({
        "client_id": env("SHAREPOINT_CLIENT_ID"),
        "client_secret": env("SHAREPOINT_CLIENT_SECRET"),
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"}).encode()
    url = f"https://login.microsoftonline.com/{env('SHAREPOINT_TENANT_ID')}/oauth2/v2.0/token"
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(url, data=body), timeout=30).read().decode())["access_token"]


class Graph:
    def __init__(self):
        self.t = token()
        u = urllib.parse.urlparse(env("SHAREPOINT_SITE_URL"))
        self.site = self.get(f"/sites/{u.netloc}:{u.path.rstrip('/')}")["id"]

    def _req(self, method, url, data=None, headers=None):
        h = {"Authorization": f"Bearer {self.t}", **(headers or {})}
        if data is not None and "Content-Type" not in h:
            h["Content-Type"] = "application/json"
        r = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, timeout=180) as x:
                raw = x.read().decode() or "{}"
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            return {"_e": e.code, "_b": e.read().decode("utf-8", "replace")[:300]}

    def get(self, path):
        return self._req("GET", "https://graph.microsoft.com/v1.0" + path)

    def drive(self, path):
        """Graph wants the path url-quoted but the colons literal."""
        return (f"https://graph.microsoft.com/v1.0/sites/{self.site}/drive/root:/"
                f"{urllib.parse.quote(path)}")

    def ensure_folder(self, path):
        if "_e" not in self.get(f"/sites/{self.site}/drive/root:/{urllib.parse.quote(path)}"):
            return
        parent, name = os.path.split(path)
        if parent:
            self.ensure_folder(parent)
        url = (self.drive(parent) + ":/children") if parent else \
              f"https://graph.microsoft.com/v1.0/sites/{self.site}/drive/root/children"
        r = self._req("POST", url, json.dumps({
            "name": name, "folder": {},
            "@microsoft.graph.conflictBehavior": "fail"}).encode())
        if "_e" in r and r["_e"] != 409:
            raise SystemExit(f"mkdir {path}: {r['_e']} {r['_b']}")

    def remote_size(self, path):
        r = self.get(f"/sites/{self.site}/drive/root:/{urllib.parse.quote(path)}")
        return None if "_e" in r else r.get("size")

    def upload(self, local, path):
        size = os.path.getsize(local)
        data = io.open(local, "rb").read()
        if size < 4 * 1024 * 1024:
            r = self._req("PUT", self.drive(path) + ":/content", data,
                          {"Content-Type": "application/octet-stream"})
            if "_e" in r:
                raise SystemExit(f"upload {path}: {r['_e']} {r['_b']}")
            return
        # Files over 4MB must go through an upload session, in chunks.
        s = self._req("POST", self.drive(path) + ":/createUploadSession",
                      json.dumps({"item": {
                          "@microsoft.graph.conflictBehavior": "replace"}}).encode())
        if "_e" in s:
            raise SystemExit(f"session {path}: {s['_e']} {s['_b']}")
        url = s["uploadUrl"]
        for start in range(0, size, CHUNK):
            end = min(start + CHUNK, size) - 1
            req = urllib.request.Request(url, data=data[start:end + 1], method="PUT",
                headers={"Content-Length": str(end - start + 1),
                         "Content-Range": f"bytes {start}-{end}/{size}"})
            try:
                urllib.request.urlopen(req, timeout=300).read()
            except urllib.error.HTTPError as e:
                raise SystemExit(f"chunk {path} {start}: {e.code} "
                                 f"{e.read().decode('utf-8','replace')[:200]}")


def human(n):
    return f"{n/1048576:.1f}MB" if n > 1048576 else f"{max(1, n//1024)}KB"


if __name__ == "__main__":
    plan_only = "--plan" in sys.argv
    g = None if plan_only else Graph()

    missing, todo, same = [], [], []
    for rel, sub in MANIFEST:
        local = os.path.join(ROOT, rel)
        if not os.path.exists(local):
            missing.append(rel)
            continue
        dest = f"{BASE}/{sub}/{os.path.basename(rel)}"
        size = os.path.getsize(local)
        if g and g.remote_size(dest) == size:
            same.append((dest, size))
        else:
            todo.append((local, dest, size))

    if missing:
        print("חסר מקומית (דלג):")
        for m in missing:
            print(f"   {m}")
        print()

    if same:
        print(f"כבר מעודכן: {len(same)} קבצים\n")

    print(f"{'יועלה' if not plan_only else 'היה מועלה'}: {len(todo)} קבצים, "
          f"{human(sum(s for _, _, s in todo))}\n")
    for _, dest, size in todo:
        print(f"   {dest}   {human(size)}")

    if plan_only or not todo:
        sys.exit(0)

    print()
    folders = sorted({os.path.dirname(d) for _, d, _ in todo})
    for f in folders:
        g.ensure_folder(f)
    for local, dest, size in todo:
        g.upload(local, dest)
        print(f"   הועלה  {dest}")
    print(f"\n-> {env('SHAREPOINT_SITE_URL')}")
