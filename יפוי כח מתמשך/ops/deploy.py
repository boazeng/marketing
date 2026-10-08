# -*- coding: utf-8 -*-
"""
Serves the ייפוי כוח מתמשך landing page from the Mac mini, the same way as
המושבה ב׳ (see its ops/deploy.py and env/MAC-MINI-APP-INSTALL.md, section 3.5):
nginx in OrbStack plus a dedicated Cloudflare tunnel container, no sudo.

    python deploy.py pull        fetch the page from SharePoint into site/index.html
    python deploy.py tunnel      ONE TIME: create the tunnel and its DNS record
    python deploy.py publish     pull -> upload -> (re)start -> check locally
    python deploy.py verify      check the public URL end to end

The page itself is not in git. The marketer edits it in SharePoint and the
lawyer approves it there, so that copy is the source and publish always takes
it fresh -- a copy in the repo would be the one that missed his last correction.
"""
import io, os, shutil, subprocess, sys, tarfile, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", "site"))
SERVER = os.path.join(HERE, "server")
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "bedek", "ops")))
from sharepoint import Graph  # noqa: E402  -- same tenant, same app credentials

APP = "zohar"
HOST = f"{APP}.newavera.co.il"
PORT = 8109                      # registry: env/MAC-MINI-APP-INSTALL.md
REMOTE = f"~/server/{APP}"
SSH = shutil.which("ssh") or "ssh"
CLOUDFLARED = "/opt/homebrew/bin/cloudflared"   # not on the non-login PATH

PAGE_DIR = "TACT/שיווק/יפוי כח מתמשך/אתר"
MARK = "אנגלנדר"                 # a 200 without the lawyer's name is the wrong page
PIXEL_ID = "1531044362163696"    # dataset `zohar-poa`, TACT NIRIM -- an id, not a secret


def ssh(cmd, stdin=None):
    r = subprocess.run([SSH, "-o", "BatchMode=yes", "mac-remote", cmd],
                       input=stdin, capture_output=True, timeout=300)
    out = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
    if r.returncode:
        raise SystemExit(f"ssh failed ({r.returncode}): {cmd}\n{out}")
    return out


def pull():
    g = Graph()
    kids = g.get(f"/sites/{g.site}/drive/root:/{urllib.parse.quote(PAGE_DIR)}:/children")
    pages = [k for k in kids.get("value", []) if k["name"].lower().endswith(".html")]
    # The folder is expected to hold exactly one page. Two means someone saved
    # a draft beside the approved one, and guessing which is live is how an
    # unapproved wording gets published under a lawyer's name.
    if len(pages) != 1:
        raise SystemExit(f"expected one .html in {PAGE_DIR}, found "
                         f"{[p['name'] for p in pages]}")
    p = pages[0]
    data = urllib.request.urlopen(p["@microsoft.graph.downloadUrl"], timeout=60).read()
    if MARK not in data.decode("utf-8", "replace"):
        raise SystemExit(f"{p['name']} does not mention {MARK} -- not publishing it")
    # The consent banner and pixel are ours, not the marketer's: they are added
    # here on every publish so a new version of her file never loses them.
    html = data.decode("utf-8")
    snippet = io.open(os.path.join(HERE, "pixel.html"), encoding="utf-8").read()
    if html.count("</body>") != 1:
        raise SystemExit(f"{p['name']}: expected exactly one </body> to inject the pixel before")
    html = html.replace("</body>", snippet.replace("__PIXEL_ID__", PIXEL_ID) + "</body>")
    # The lead form goes just above the page's own call-to-action band. If the
    # marketer renames that section, stop: a page silently published without
    # its form is leads lost with nobody told.
    anchor = '<section id="contact">'
    if html.count(anchor) != 1:
        raise SystemExit(f"{p['name']}: expected exactly one {anchor} to place the lead form")
    form = io.open(os.path.join(HERE, "lead-form.html"), encoding="utf-8").read()
    html = html.replace(anchor, form + anchor)
    os.makedirs(SITE, exist_ok=True)
    io.open(os.path.join(SITE, "index.html"), "w", encoding="utf-8", newline="").write(html)
    print(f"  {len(data):>7}  {p['name']}  (modified {p['lastModifiedDateTime']})")


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
    pull()
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
               f"&& grep -c '{MARK}' /tmp/{APP}.html")
    print(f"   local: {code.replace(chr(10), '  name-hits=')}")


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
              f"name={MARK in body}")
    print(ssh(f"~/.orbstack/bin/docker logs {APP}-tunnel 2>&1 | grep -c Registered"),
          "tunnel connections registered")


if __name__ == "__main__":
    {"pull": pull, "publish": publish, "tunnel": tunnel, "verify": verify}[
        sys.argv[1] if len(sys.argv) > 1 else "publish"]()
