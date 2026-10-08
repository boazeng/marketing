# -*- coding: utf-8 -*-
"""
Sets the Page's profile picture and cover from social/out/.

    python assets.py            first -- this only uploads what that rendered
    python upload_assets.py

The Page is public, so both are visible the moment this returns.

The Page token is derived from the system-user token on every run (me/accounts)
rather than stored: it never expires on its own, but it dies with the system
user's token, and a second copy in .env would be the one nobody rotated.
"""
import io, json, os, sys, urllib.error, urllib.parse, urllib.request, uuid

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")

PAGE_ID = "1282274348312668"
SYSTEM_TOKEN = "META_PAGE_TOKEN_BEDEK"      # Tact publisher, TACT NIRIM
API = "https://graph.facebook.com/v21.0/"


def env(key):
    for raw in io.open(ENV, encoding="utf-8", errors="replace").read().splitlines():
        l = raw.strip().lstrip("\ufeff")
        if l.startswith(key + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{key} not in the shared .env")


def call(path, fields=None, file=None, method="GET"):
    url, data, headers = API + path, None, {}
    if method == "GET":
        url += "?" + urllib.parse.urlencode(fields or {})
    elif file:
        b = uuid.uuid4().hex
        parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
                 for k, v in (fields or {}).items()]
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="source"; '
                     f'filename="{os.path.basename(file)}"\r\n'
                     f'Content-Type: image/png\r\n\r\n'.encode()
                     + io.open(file, "rb").read() + b"\r\n")
        data = b"".join(parts) + f"--{b}--\r\n".encode()
        headers["Content-Type"] = f"multipart/form-data; boundary={b}"
    else:
        data = urllib.parse.urlencode(fields or {}).encode()
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        return json.loads(urllib.request.urlopen(r, timeout=120).read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path}: {e.code} "
                         f"{json.loads(e.read()).get('error', {}).get('message')}")


if __name__ == "__main__":
    pages = call("me/accounts", {"fields": "id,access_token", "limit": 100,
                                 "access_token": env(SYSTEM_TOKEN)})["data"]
    tok = next((p["access_token"] for p in pages if p["id"] == PAGE_ID), None)
    if not tok:
        raise SystemExit("system user is not assigned to the Page -- see meta-setup.md")

    call(f"{PAGE_ID}/picture", {"access_token": tok},
         os.path.join(OUT, "profile.png"), "POST")
    print("   profile set")

    # A cover is a photo first and a setting second. no_story keeps the upload
    # out of the feed -- otherwise the Page's first post is its own cover.
    photo = call(f"{PAGE_ID}/photos",
                 {"access_token": tok, "published": "false", "no_story": "true"},
                 os.path.join(OUT, "cover.png"), "POST")
    call(PAGE_ID, {"access_token": tok, "cover": photo["id"]}, method="POST")
    print("   cover set")

    got = call(PAGE_ID, {"fields": "cover{source},picture{is_silhouette}",
                         "access_token": tok})
    print("   read back: cover", "ok" if got.get("cover") else "MISSING",
          "· profile", "MISSING" if got["picture"]["data"]["is_silhouette"] else "ok")
    print(f"\n-> https://www.facebook.com/{PAGE_ID}")
