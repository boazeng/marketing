# -*- coding: utf-8 -*-
"""
Cloudflare DNS for yazam-il.com.

    python cf.py list
    python cf.py ensure <type> <name> <content> [proxied:true|false]

The token lives in the shared .env as CLOUDFLARE_API_TOKEN and is scoped to
Zone:DNS:Edit on this one zone -- it cannot touch newavera.co.il.
"""
import io, json, os, sys, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

# The shared secrets file. Override with TACT_ENV on a machine where it
# lives elsewhere -- nothing in this repo may ever contain a secret.
ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")
ZONE_NAME = "yazam-il.com"
API = "https://api.cloudflare.com/client/v4"


def token():
    # Parsed rather than grepped: the file has no trailing newline and may use
    # CRLF, both of which quietly defeat a naive line match.
    for raw in io.open(ENV, encoding="utf-8", errors="replace").read().splitlines():
        line = raw.strip().lstrip("\ufeff")
        if line.startswith("CLOUDFLARE_API_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("CLOUDFLARE_API_TOKEN not found in the shared .env")


TOKEN = token()


def call(path, method="GET", body=None):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def zone_id():
    d = call(f"/zones?name={ZONE_NAME}")
    if not d.get("success") or not d["result"]:
        raise SystemExit(f"cannot read the zone: {d.get('errors')}")
    return d["result"][0]["id"]


def records(zid):
    return call(f"/zones/{zid}/dns_records?per_page=100").get("result", [])


def txt_key(content):
    """The identity of a TXT record: everything before the first '='.

    `v=spf1 ...`, `facebook-domain-verification=...` and `google-site-...` all
    legitimately live on the same name at the same time. Matching TXT records
    on name+type alone treats them as one record and silently overwrites a
    live SPF policy -- which is exactly what happened here once."""
    return content.strip().strip('"').split("=", 1)[0].strip().lower()


def ensure(zid, rtype, name, content, proxied):
    fq = ZONE_NAME if name in ("@", ZONE_NAME) else f"{name}.{ZONE_NAME}"
    body = {"type": rtype, "name": fq, "content": content,
            "ttl": 1, "proxied": proxied}
    existing = [r for r in records(zid) if r["name"] == fq and r["type"] == rtype]
    if rtype == "TXT":
        existing = [r for r in existing if txt_key(r["content"]) == txt_key(content)]
    if existing:
        d = call(f"/zones/{zid}/dns_records/{existing[0]['id']}", "PUT", body)
        verb = "updated"
    else:
        d = call(f"/zones/{zid}/dns_records", "POST", body)
        verb = "created"
    if not d.get("success"):
        raise SystemExit(f"{fq}: {d.get('errors')}")
    r = d["result"]
    print(f"   {verb:8} {r['type']:6} {r['name']:26} -> {r['content']}"
          f"   proxy={'ON' if r.get('proxied') else 'DNS only'}")


if __name__ == "__main__":
    zid = zone_id()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        print(f"zone {ZONE_NAME} ({zid})\n")
        for r in sorted(records(zid), key=lambda x: (x["type"], x["name"])):
            print(f"   {r['type']:6} {r['name']:44} -> {r['content'][:60]:62}"
                  f" {'proxied' if r.get('proxied') else ''}")
    elif cmd == "ensure":
        rtype, name, content = sys.argv[2], sys.argv[3], sys.argv[4]
        proxied = len(sys.argv) > 5 and sys.argv[5].lower() == "true"
        ensure(zid, rtype, name, content, proxied)
    else:
        raise SystemExit(__doc__)
