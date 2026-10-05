# -*- coding: utf-8 -*-
"""
Serves the המושבה ב׳ site from the Mac mini, the way every newavera.co.il app
is served (env/MAC-MINI-APP-INSTALL.md, section 3.5): nginx in OrbStack plus
a dedicated Cloudflare tunnel container, so nothing here ever needs sudo.

    python deploy.py assets      pull the images from SharePoint into site/assets, as WebP
    python deploy.py tunnel      ONE TIME: create the tunnel and its DNS record
    python deploy.py publish     assets -> upload site -> (re)start -> check locally
    python deploy.py verify      check the public URL end to end

Images come from SharePoint, never git: the repo holds what produces, and the
logo and photos are made things that live with the rest of the brand files there.
"""
import io, os, shutil, subprocess, sys, tarfile, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", "site"))
SERVER = os.path.join(HERE, "server")
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "bedek", "ops")))
from sharepoint import Graph  # noqa: E402  -- same tenant, same app credentials

APP = "moshava-b"
HOST = f"{APP}.newavera.co.il"
PORT = 8108                      # registry: env/MAC-MINI-APP-INSTALL.md
REMOTE = f"~/server/{APP}"
SSH = shutil.which("ssh") or "ssh"
CLOUDFLARED = "/opt/homebrew/bin/cloudflared"   # not on the non-login PATH

# The landing page's images, as the designer left them in SharePoint. Each is
# resized and re-encoded here: the originals total ~1.7MB (the logo alone is
# 370KB), and on a phone arriving from an ad that weight is paid for in leads.
ASSETS_DIR = "TACT/שיווק/מכירת קרקע בטבריה/אתר/moshava-b-landing/assets"
#   source file                      -> (output, max width, quality)
ASSETS = {
    "favicon.png":                   ("favicon.png", None, None),      # as is
    "logo-gold.png":                 ("logo-gold.webp", 440, 90),      # shown at 220px, 2x
    "hero-brochure.jpg":             ("hero-brochure.webp", 1600, 72), # behind an overlay
    "photo-drone-kinneret-1.png":    ("photo-drone-kinneret-1.webp", 1200, 80),
    "photo-drone-poria-ridge-1.png": ("photo-drone-poria-ridge-1.webp", 1200, 80),
    "photo-land-plots-green-1.png":  ("photo-land-plots-green-1.webp", 1200, 80),
}
# Link previews want a 1200x630 JPEG at an absolute URL; scrapers are still
# unreliable with WebP.
OG_SOURCE = "photo-drone-kinneret-1.png"


def ssh(cmd, stdin=None):
    r = subprocess.run([SSH, "-o", "BatchMode=yes", "mac-remote", cmd],
                       input=stdin, capture_output=True, timeout=300)
    out = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
    if r.returncode:
        raise SystemExit(f"ssh failed ({r.returncode}): {cmd}\n{out}")
    return out


def assets():
    from PIL import Image
    g = Graph()
    out_dir = os.path.join(SITE, "assets")
    os.makedirs(out_dir, exist_ok=True)

    def fetch(name):
        url = (f"https://graph.microsoft.com/v1.0/sites/{g.site}/drive/root:/"
               f"{urllib.parse.quote(ASSETS_DIR + '/' + name)}:/content")
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {g.t}"})
        return urllib.request.urlopen(req, timeout=120).read()

    for src, (out, width, quality) in ASSETS.items():
        raw = fetch(src)
        dest = os.path.join(out_dir, out)
        if width is None:
            open(dest, "wb").write(raw)
        else:
            im = Image.open(io.BytesIO(raw))
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            im.save(dest, "WEBP", quality=quality, method=6)
        print(f"  {len(raw) // 1024:>5}KB -> {os.path.getsize(dest) // 1024:>4}KB  assets/{out}")
        if src == OG_SOURCE:
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            scale = max(1200 / im.width, 630 / im.height)
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
            left, top = (im.width - 1200) // 2, (im.height - 630) // 2
            im.crop((left, top, left + 1200, top + 630)).save(
                os.path.join(out_dir, "og.jpg"), "JPEG", quality=85, optimize=True)
            print(f"          -> {os.path.getsize(os.path.join(out_dir, 'og.jpg')) // 1024:>4}KB  assets/og.jpg")


def bundle():
    """site/ + server config as one tar. site/ is emptied on the Mac first so
    a deleted file does not linger; tunnel/ there is never touched."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        t.add(SITE, arcname="site")
        for f in ("docker-compose.yml", "nginx.conf"):
            t.add(os.path.join(SERVER, f), arcname=f)
    return buf.getvalue()


def publish():
    assets()
    data = bundle()
    print(f"-> uploading {len(data) // 1024}KB to mac-remote:{REMOTE}")
    # Empty site/ in place -- never `rm -rf site`: nginx bind-mounts the
    # directory itself, and a recreated one leaves the running container
    # holding the deleted inode and answering 404 to everything.
    ssh(f"mkdir -p {REMOTE}/site && cd {REMOTE} && find site -mindepth 1 -delete "
        f"&& tar -xzf -", stdin=data)
    if "creds.json" not in ssh(f"ls {REMOTE}/tunnel 2>/dev/null || true"):
        print("!! no tunnel yet -- run `python deploy.py tunnel` once; serving locally only")
        ssh(f"cd {REMOTE} && ~/.orbstack/bin/docker compose up -d {APP}")
    else:
        ssh(f"cd {REMOTE} && ~/.orbstack/bin/docker compose up -d")
    # Check the served page, not the exit code: a 200 with the wrong body is
    # still a failure.
    code = ssh(f"curl -s -o /tmp/{APP}.html -w '%{{http_code}}\\n' http://127.0.0.1:{PORT}/ "
               f"&& grep -c 'המושבה ב' /tmp/{APP}.html")
    print(f"   local: {code.replace(chr(10), '  brand-hits=')}")


def tunnel():
    if "creds.json" in ssh(f"ls {REMOTE}/tunnel 2>/dev/null || true"):
        raise SystemExit("tunnel already exists -- nothing to do")
    out = ssh(f"{CLOUDFLARED} tunnel create {APP}")
    tid = next(w for w in out.split() if w.count("-") == 4 and len(w) == 36)
    ssh(f"""mkdir -p {REMOTE}/tunnel && cp ~/.cloudflared/{tid}.json {REMOTE}/tunnel/creds.json \
&& chmod 600 {REMOTE}/tunnel/creds.json && cat > {REMOTE}/tunnel/config.yml <<'YML'
tunnel: {tid}
credentials-file: /etc/cloudflared/creds.json
ingress:
  - hostname: {HOST}
    service: http://{APP}:80
  - service: http_status:404
YML""")
    # No --overwrite-dns: if the name is already taken, fail loudly rather
    # than silently repoint someone else's record.
    print(ssh(f"{CLOUDFLARED} tunnel route dns {tid} {HOST}"))
    print(f"tunnel {tid} -> {HOST}. Now: python deploy.py publish")


def verify():
    req = urllib.request.Request(f"https://{HOST}/", headers={"User-Agent": "deploy-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "replace")
        print(f"https://{HOST}/  {r.status}  server={r.headers.get('Server')}  "
              f"brand={'המושבה ב' in body}")
    print(ssh(f"~/.orbstack/bin/docker logs {APP}-tunnel 2>&1 | grep -c Registered"),
          "tunnel connections registered")


if __name__ == "__main__":
    {"assets": assets, "publish": publish, "tunnel": tunnel, "verify": verify}[
        sys.argv[1] if len(sys.argv) > 1 else "publish"]()
