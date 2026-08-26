# -*- coding: utf-8 -*-
"""
Lead proxy for yazam-il.com.

The browser cannot hold the CRM key -- anything in a VITE_ variable ships to
every visitor -- so the form posts here and this function forwards to
TACT-CRM with the key it reads from SSM.

Two rules shape everything below:

  1. A lead is never lost. The Telegram notification is sent even when the CRM
     write fails, and the caller still gets a 200 in that case. A lead that
     vanishes because a downstream system had a bad minute is the single worst
     outcome this whole marketing effort can produce.

  2. Nothing here trusts the browser. The client-side validation exists to give
     a person a fast, kind error; it is not a control. Everything is checked
     again here.

Standard library only, deliberately: no build step, no Docker, no layer.
"""
import hmac
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

CRM_URL = os.environ.get("CRM_URL", "https://crm-db.newavera.co.il/api/v1/customers")
ALLOWED_ORIGINS = {
    "https://yazam-il.com",
    "https://www.yazam-il.com",
    "http://localhost:5340",  # dev
}
MAX_BODY = 8_000            # a real lead is ~500 bytes
# The HTTP API in front of this function is reachable from the internet as well
# as through CloudFront. The CDN attaches this header; anything without it did
# not come through the front door and is refused.
EDGE_PARAM = os.environ.get("EDGE_SECRET_PARAM")
MIN_FILL_SECONDS = 3        # a human cannot complete this form faster

_secrets: dict[str, str] = {}


def secret(name: str) -> str:
    """SSM parameter, cached for the life of the execution environment."""
    if name in _secrets:
        return _secrets[name]
    import boto3  # provided by the Lambda runtime

    val = boto3.client("ssm").get_parameter(Name=name, WithDecryption=True)
    _secrets[name] = val["Parameter"]["Value"]
    return _secrets[name]


# ------------------------------------------------------------------ helpers

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")


def clean_phone(v: str) -> str:
    return re.sub(r"[\s\-()]", "", v or "").replace("+972", "0", 1)


def valid_phone(v: str) -> bool:
    return bool(re.fullmatch(r"0(5\d|7\d|[2-4]|[89])\d{7}", clean_phone(v)))


def cors(origin: str | None) -> dict:
    allow = origin if origin in ALLOWED_ORIGINS else "https://yazam-il.com"
    return {
        "Access-Control-Allow-Origin": allow,
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json; charset=utf-8",
    }


def reply(code: int, body: dict, origin: str | None):
    return {"statusCode": code, "headers": cors(origin),
            "body": json.dumps(body, ensure_ascii=False)}


def post_json(url: str, payload: dict, headers: dict, timeout: int = 8):
    req = urllib.request.Request(
        url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


# ------------------------------------------------------------- destinations

def to_crm(lead: dict) -> tuple[bool, str]:
    """The CRM's customer is the COMPANY; the person who filled the form is the
    contact. `external_ref` keys on the email so a second submission from the
    same person updates the record instead of creating a twin."""
    contact = [f"איש קשר: {lead['name']}"]
    if lead.get("projects"):
        contact.append(f"פרויקטים פעילים: {lead['projects']}")
    if lead.get("note"):
        contact.append(f"הערה: {lead['note']}")
    contact.append(f"מקור: {lead['source']} · yazam-il.com")
    for k, v in (lead.get("campaign") or {}).items():
        contact.append(f"{k}: {v}")

    payload = {
        "full_name": lead["company"],
        "customer_type": "organization",
        "company_name": lead["company"],
        "phone": clean_phone(lead["phone"]),
        "email": lead["email"],
        "notes": "\n".join(contact),
        "status": "active",
        "source": "api",
        "external_ref": f"yazam-il:{lead['email'].lower()}",
    }
    try:
        code, body = post_json(CRM_URL, payload,
                               {"X-API-Key": secret(os.environ["CRM_KEY_PARAM"])})
        return 200 <= code < 300, f"{code} {body[:200]}"
    except urllib.error.HTTPError as e:
        return False, f"{e.code} {e.read().decode('utf-8', 'replace')[:200]}"
    except Exception as e:                      # noqa: BLE001 - never raise past here
        return False, f"{type(e).__name__}: {e}"


def to_telegram(lead: dict, crm_ok: bool, crm_detail: str) -> bool:
    """Sent for every lead, not only on failure -- it is how a person finds out
    a lead arrived at all."""
    head = "🟢 ליד חדש" if crm_ok else "🔴 ליד חדש — הכתיבה ל-CRM נכשלה"
    lines = [
        f"*{head}*",
        f"חברה: {lead['company']}",
        f"איש קשר: {lead['name']}",
        f"טלפון: {clean_phone(lead['phone'])}",
        f"אימייל: {lead['email']}",
    ]
    if lead.get("projects"):
        lines.append(f"פרויקטים: {lead['projects']}")
    if lead.get("note"):
        lines.append(f"הערה: {lead['note']}")
    lines.append(f"עמוד: {lead['source']}")
    if lead.get("campaign"):
        lines.append("קמפיין: " + ", ".join(f"{k}={v}" for k, v in lead["campaign"].items()))
    if not crm_ok:
        lines.append(f"\n⚠️ שגיאת CRM: `{crm_detail}`\nהליד לא נשמר — טפל ידנית.")

    try:
        token = secret(os.environ["TG_TOKEN_PARAM"])
        chat = secret(os.environ["TG_CHAT_PARAM"])
        post_json(f"https://api.telegram.org/bot{token}/sendMessage",
                  {"chat_id": chat, "text": "\n".join(lines), "parse_mode": "Markdown"},
                  {}, timeout=6)
        return True
    except Exception:                            # noqa: BLE001
        return False


# ------------------------------------------------------------------ handler

def lambda_handler(event, _context):
    http = (event.get("requestContext") or {}).get("http") or {}
    method = http.get("method", "POST")
    origin = (event.get("headers") or {}).get("origin")

    if method == "OPTIONS":
        return {"statusCode": 204, "headers": cors(origin), "body": ""}
    if method != "POST":
        return reply(405, {"error": "method not allowed"}, origin)

    if EDGE_PARAM:
        given = (event.get("headers") or {}).get("x-origin-token")
        try:
            expected = secret(EDGE_PARAM)
        except Exception:                        # noqa: BLE001
            expected = None
        # `compare_digest` rather than `!=` -- this is a secret comparison.
        if not expected or not given or not hmac.compare_digest(given, expected):
            return reply(403, {"error": "forbidden"}, origin)

    raw = event.get("body") or ""
    if len(raw) > MAX_BODY:
        return reply(413, {"error": "body too large"}, origin)

    try:
        lead = json.loads(raw)
    except json.JSONDecodeError:
        return reply(400, {"error": "invalid json"}, origin)

    # Honeypot: a field no human sees and no human fills. Answer 200 so the bot
    # believes it succeeded and does not come back looking for a weakness.
    if (lead.get("website") or "").strip():
        return reply(200, {"ok": True}, origin)

    # Anything submitted within a few seconds of the page rendering was not
    # typed by a person.
    started = lead.get("startedAt")
    if isinstance(started, (int, float)) and time.time() * 1000 - started < MIN_FILL_SECONDS * 1000:
        return reply(200, {"ok": True}, origin)

    lead = {k: (v.strip() if isinstance(v, str) else v) for k, v in lead.items()}

    missing = [f for f in ("name", "company", "phone", "email") if not lead.get(f)]
    if missing:
        return reply(400, {"error": "missing", "fields": missing}, origin)
    if not EMAIL_RE.match(lead["email"]):
        return reply(400, {"error": "bad email"}, origin)
    if not valid_phone(lead["phone"]):
        return reply(400, {"error": "bad phone"}, origin)
    if lead.get("source") not in ("site", "landing"):
        lead["source"] = "site"

    crm_ok, crm_detail = to_crm(lead)
    tg_ok = to_telegram(lead, crm_ok, crm_detail)

    if not crm_ok:
        print(json.dumps({"level": "error", "crm": crm_detail,
                          "telegram": tg_ok, "email": lead["email"]}, ensure_ascii=False))

    # 200 even when the CRM refused, PROVIDED the notification landed: a person
    # has the lead and the visitor should not be asked to fill the form again.
    # If both failed, tell the truth -- the site shows its fallback address.
    if not crm_ok and not tg_ok:
        return reply(502, {"error": "delivery failed"}, origin)
    return reply(200, {"ok": True}, origin)
