# -*- coding: utf-8 -*-
"""
Lead proxy for every TACT marketing site (yazam-il.com, moshava-b, ...).

The browser cannot hold a key -- anything in a VITE_ variable ships to every
visitor -- so the form posts here and this function forwards the lead with
the keys it reads from SSM.

Where a lead goes:

    task-manager  the system of record. The marketer works the lead there,
                through its statuses. Every project lands in the same table,
                told apart by `project`.
    Telegram    always, so a person learns a lead arrived at all.
    TACT-CRM    bedek only. Secondary: the CRM's customer is a COMPANY, which
                a private buyer of a plot is not.

Two rules shape everything below:

  1. A lead is never lost. The Telegram notification is sent even when the
     task-manager write fails, and the caller still gets a 200 in that case. A
     lead that vanishes because a downstream system had a bad minute is the
     single worst outcome this whole marketing effort can produce.

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
TASK_URL = os.environ.get("TASK_URL")               # unset = destination off
TASK_TOKEN_PARAM = os.environ.get("TASK_TOKEN_PARAM")
TASK_TOKEN_HEADER = os.environ.get("TASK_TOKEN_HEADER", "X-Lead-Token")

# One entry per marketing site. `required` is what THAT form collects -- a
# private buyer in Tiberias has no company and is not asked for an email.
# `details` are the form's own extra fields, passed through with their label.
PROJECTS = {
    "bedek": {
        "name": "TACT בדק",
        "origins": {"https://yazam-il.com", "https://www.yazam-il.com",
                    "http://localhost:5340"},  # dev
        "required": ("name", "company", "phone", "email"),
        "details": {"projects": "פרויקטים פעילים"},
        "crm": True,
    },
    "moshava-b": {
        "name": "המושבה ב׳ טבריה",
        "origins": {"https://moshava-b.newavera.co.il"},
        "required": ("name", "phone"),
        "details": {"interest": "עניין"},
        "crm": False,
    },
    # Name and phone only, on purpose: a free-text field on a lawyer's page
    # invites family and medical detail into a table the marketer works in.
    "zohar": {
        "name": "ייפוי כוח מתמשך",          # as it appears in task-manager (Boaz)
        "origins": {"https://zohar.newavera.co.il"},
        "required": ("name", "phone"),
        "details": {},
        "crm": False,
    },
}
DEFAULT_PROJECT = "bedek"       # the first site, which never sent `project`
ALLOWED_ORIGINS = set().union(*(p["origins"] for p in PROJECTS.values()))
CHANNELS = ("site", "landing")

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
    """Local form, digits only. `972…` is accepted with or without the plus:
    the Tiberias form takes any 9-12 digits, and a number refused here is a
    lead the visitor is told failed to send."""
    p = re.sub(r"[\s\-().]", "", v or "")
    if p.startswith("+972"):
        return "0" + p[4:].lstrip("0")
    if p.startswith("972") and len(p) >= 11:
        return "0" + p[3:].lstrip("0")
    return p


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
        # A named agent, because the default "Python-urllib" is refused by
        # Cloudflare (403, error 1010) before the request reaches task-manager.
        headers={"Content-Type": "application/json",
                 "User-Agent": "tact-lead-proxy/1.0", **headers}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def project_of(lead: dict, origin: str | None) -> str:
    """The form may name its project; otherwise the Origin does. Neither is a
    control -- a forged project only mislabels the forger's own lead."""
    if lead.get("project") in PROJECTS:
        return lead["project"]
    for slug, p in PROJECTS.items():
        if origin in p["origins"]:
            return slug
    return DEFAULT_PROJECT


# ------------------------------------------------------------- destinations

def to_task(lead: dict) -> tuple[bool, str]:
    """task-manager, the system of record. `external_ref` keys on project + phone,
    so a second submission from the same person is appended to the existing
    lead's activity instead of opening a twin for the marketer to chase."""
    if not TASK_URL or not TASK_TOKEN_PARAM:
        return False, "אין כרגע מערכת רישום מחוברת"
    proj = PROJECTS[lead["project"]]
    payload = {
        "project": lead["project"],
        "project_name": proj["name"],
        "channel": lead["source"],
        "name": lead["name"],
        "phone": clean_phone(lead["phone"]),
        "email": lead.get("email") or "",
        "company": lead.get("company") or "",
        "message": lead.get("note") or "",
        "details": {label: lead[k] for k, label in proj["details"].items() if lead.get(k)},
        "campaign": lead.get("campaign") or {},
        "page_url": lead.get("page") or "",
        "referrer": lead.get("referrer") or "",
        "external_ref": f"{lead['project']}:{clean_phone(lead['phone'])}",
    }
    try:
        code, body = post_json(TASK_URL, payload,
                               {TASK_TOKEN_HEADER: secret(TASK_TOKEN_PARAM)}, timeout=6)
        return 200 <= code < 300, f"{code} {body[:200]}"
    except urllib.error.HTTPError as e:
        return False, f"{e.code} {e.read().decode('utf-8', 'replace')[:200]}"
    except Exception as e:                      # noqa: BLE001 - never raise past here
        return False, f"{type(e).__name__}: {e}"


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
        # Short: with task-manager (6s) and Telegram (6s) ahead of it, the three
        # must fit inside the function's 20s.
        code, body = post_json(CRM_URL, payload,
                               {"X-API-Key": secret(os.environ["CRM_KEY_PARAM"])}, timeout=4)
        return 200 <= code < 300, f"{code} {body[:200]}"
    except urllib.error.HTTPError as e:
        return False, f"{e.code} {e.read().decode('utf-8', 'replace')[:200]}"
    except Exception as e:                      # noqa: BLE001 - never raise past here
        return False, f"{type(e).__name__}: {e}"


def to_telegram(lead: dict, saved: bool, detail: str) -> bool:
    """Sent for every lead, not only on failure -- it is how a person finds out
    a lead arrived at all."""
    proj = PROJECTS[lead["project"]]
    head = "🟢 ליד חדש" if saved else "🔴 ליד חדש — הכתיבה ל-task-manager נכשלה"
    lines = [f"{head} · {proj['name']}"]
    if lead.get("company"):
        lines.append(f"חברה: {lead['company']}")
    lines.append(f"איש קשר: {lead['name']}")
    lines.append(f"טלפון: {clean_phone(lead['phone'])}")
    if lead.get("email"):
        lines.append(f"אימייל: {lead['email']}")
    for k, label in proj["details"].items():
        if lead.get(k):
            lines.append(f"{label}: {lead[k]}")
    if lead.get("note"):
        lines.append(f"הערה: {lead['note']}")
    lines.append(f"עמוד: {lead['source']}")
    if lead.get("campaign"):
        lines.append("קמפיין: " + ", ".join(f"{k}={v}" for k, v in lead["campaign"].items()))
    if not saved:
        lines.append(f"\n⚠️ שגיאת task-manager: {detail.strip()}\nהליד לא נשמר — טפל ידנית.")

    try:
        token = secret(os.environ["TG_TOKEN_PARAM"])
        chat = secret(os.environ["TG_CHAT_PARAM"])
        post_json(f"https://api.telegram.org/bot{token}/sendMessage",
                  # Plain text, no parse_mode. With Markdown, the "_" in
                  # "utm_source" is an unclosed italic and Telegram rejects the
                  # whole message -- so exactly the leads that came from a paid
                  # ad were the ones nobody was told about.
                  {"chat_id": chat, "text": "\n".join(lines)},
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
    if not isinstance(lead, dict):
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
    lead["project"] = project_of(lead, origin)
    proj = PROJECTS[lead["project"]]

    missing = [f for f in proj["required"] if not lead.get(f)]
    if missing:
        return reply(400, {"error": "missing", "fields": missing}, origin)
    if lead.get("email") and not EMAIL_RE.match(lead["email"]):
        return reply(400, {"error": "bad email"}, origin)
    if not valid_phone(lead["phone"]):
        return reply(400, {"error": "bad phone"}, origin)
    if lead.get("source") not in CHANNELS:
        lead["source"] = "site"
    if not isinstance(lead.get("campaign"), dict):
        lead["campaign"] = {}

    saved, detail = to_task(lead)
    tg_ok = to_telegram(lead, saved, detail)

    # Secondary, so it runs after the person has been told and never decides
    # the answer.
    crm_detail = None
    if proj["crm"]:
        _, crm_detail = to_crm(lead)

    if saved:
        # task-manager's own answer ({"id", "created"}). Without it, "the lead is
        # not in the table" cannot be told apart from "it was merged into an
        # existing lead with the same phone".
        print(json.dumps({"level": "info", "project": lead["project"], "task": detail,
                          "telegram": tg_ok}, ensure_ascii=False))
    else:
        # The whole lead, not just the phone: when the system of record is
        # down this log line and the Telegram message are the only two copies,
        # and Telegram may have failed too. Enough here to re-enter it by hand.
        keep = ("name", "phone", "email", "company", "note", "source", "page",
                "referrer", "campaign", *proj["details"])
        print(json.dumps({"level": "error", "project": lead["project"], "task": detail,
                          "crm": crm_detail, "telegram": tg_ok,
                          "lead": {k: lead[k] for k in keep if lead.get(k)}},
                         ensure_ascii=False))

    # 200 even when task-manager refused, PROVIDED the notification landed: a
    # person has the lead and the visitor should not be asked to fill the form
    # again. If both failed, tell the truth -- the site shows its fallback.
    if not saved and not tg_ok:
        return reply(502, {"error": "delivery failed"}, origin)
    return reply(200, {"ok": True}, origin)
