# -*- coding: utf-8 -*-
"""
The shared WhatsApp lead line: one number (054-696-1875, "Urban Group
Marketing") serving every campaign.

    customer -> WhatsApp -> Meta webhook -> this function
                                              |- which campaign?
                                              |- task-manager  (system of record)
                                              |- Telegram      (always sent)
                                              '- one reply to the customer

Three decisions built into the code:

1. A lead is never lost to a failed write. Telegram is sent whether or not
   task-manager took the lead, and says which.
2. The customer is remembered. The first message names the campaign (the
   prefilled text of a wa.me link, or the ad a Click-to-WhatsApp message came
   from); later messages rarely do. The campaign is stored per phone so a
   bare "מתי אפשר לדבר?" lands on the same lead instead of opening a second.
3. One auto-reply per conversation, not per message. Someone who writes three
   lines in a row gets one answer.

A lead from here and one from the site's form share an `external_ref`
("<project>:<phone>"), so task-manager folds them into a single row.

There is no signature check: the Meta app's secret is not available to us.
The door is a long random path segment instead -- see deploy.py.
"""
import hmac
import json
import os
import re
import time
import urllib.error
import urllib.request

TASK_URL = os.environ.get("TASK_URL")               # unset = destination off
TASK_TOKEN_PARAM = os.environ.get("TASK_TOKEN_PARAM")
TASK_TOKEN_HEADER = os.environ.get("TASK_TOKEN_HEADER", "X-Lead-Token")
PHONE_ID = os.environ.get("WA_PHONE_ID")
TABLE = os.environ.get("TABLE")
GRAPH = "https://graph.facebook.com/v21.0"

REPLY_GAP = 12 * 3600       # one auto-reply per conversation
SEEN_TTL = 3 * 86400        # Meta retries a webhook for hours, not days

# One entry per campaign. `name` must match the site form's project name in
# the lead proxy (bedek/ops/lead-proxy/handler.py) -- it is the "פרויקט"
# column the marketer filters by. Adding a campaign is adding a block here.
CAMPAIGNS = {
    "moshava-b": {
        "name": "המושבה ב׳ טבריה",
        "keywords": ("מושבה", "טבריה", "פוריה", "moshava"),
        "reply": ("שלום! תודה שפנית בנושא המושבה ב׳ בטבריה 🌿\n"
                  "קיבלנו את הפנייה ונחזור אליך בהקדם עם כל הפרטים."),
    },
}
# Wrote in without naming a project and has no history. Filed where a person
# will see it, and asked -- never guessed into a campaign.
GENERAL = {
    "name": "פנייה כללית בוואטסאפ",
    "reply": ("שלום! תודה שפנית ל-Urban Group Marketing.\n"
              "באיזה פרויקט נוכל לעזור? נחזור אליך בהקדם."),
}

_secrets: dict[str, str] = {}
_table = None


def secret(name: str) -> str:
    """SSM parameter, cached for the life of the execution environment."""
    if name not in _secrets:
        import boto3  # provided by the Lambda runtime
        _secrets[name] = boto3.client("ssm").get_parameter(
            Name=name, WithDecryption=True)["Parameter"]["Value"]
    return _secrets[name]


def table():
    global _table
    if _table is None:
        import boto3
        _table = boto3.resource("dynamodb").Table(TABLE)
    return _table


# ------------------------------------------------------------------ helpers

def local_phone(wa_id: str) -> str:
    """972501234567 -> 0501234567, the form the site's leads are keyed by."""
    d = re.sub(r"\D", "", wa_id or "")
    return "0" + d[3:] if d.startswith("972") else d


def post_json(url: str, payload: dict, headers: dict, timeout: int = 8):
    req = urllib.request.Request(
        url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        # A named agent: Cloudflare refuses the default "Python-urllib" (403,
        # error 1010) before the request ever reaches task-manager.
        headers={"Content-Type": "application/json",
                 "User-Agent": "tact-wa-leads/1.0", **headers}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def text_of(msg: dict) -> str:
    """What the customer sent, as one line a marketer can read."""
    t = msg.get("type")
    if t == "text":
        return (msg.get("text") or {}).get("body", "")
    if t == "button":
        return (msg.get("button") or {}).get("text", "")
    if t == "interactive":
        i = msg.get("interactive") or {}
        return ((i.get("button_reply") or i.get("list_reply") or {}).get("title", ""))
    caption = (msg.get(t) or {}).get("caption") if isinstance(msg.get(t), dict) else ""
    label = {"image": "תמונה", "audio": "הודעה קולית", "video": "וידאו",
             "document": "מסמך", "location": "מיקום", "contacts": "איש קשר",
             "sticker": "מדבקה"}.get(t, t or "הודעה")
    return f"[{label}]" + (f" {caption}" if caption else "")


def campaign_of(text: str, referral: dict, known: str | None) -> str | None:
    """The ad's own text first (it cannot be edited by the customer), then the
    message, then what this phone was last filed under."""
    hay = " ".join([text or "", referral.get("headline", ""), referral.get("body", ""),
                    referral.get("source_url", "")]).lower()
    for slug, c in CAMPAIGNS.items():
        if any(k in hay for k in c["keywords"]):
            return slug
    return known


# -------------------------------------------------------------------- state

def first_sight(message_id: str) -> bool:
    """False when Meta is redelivering a message already handled."""
    from botocore.exceptions import ClientError
    try:
        table().put_item(
            Item={"pk": f"msg#{message_id}", "ttl": int(time.time()) + SEEN_TTL},
            ConditionExpression="attribute_not_exists(pk)")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise


def contact(phone: str) -> dict:
    return table().get_item(Key={"pk": f"phone#{phone}"}).get("Item") or {}


def remember(phone: str, project: str | None, replied: bool, prior: dict):
    item = {"pk": f"phone#{phone}",
            "project": project or prior.get("project") or "",
            "replied_at": int(time.time()) if replied else int(prior.get("replied_at", 0))}
    table().put_item(Item=item)


# ------------------------------------------------------------- destinations

def to_task(project: str, proj: dict, name: str, phone: str, text: str,
            referral: dict) -> tuple[bool, str]:
    if not TASK_URL or not TASK_TOKEN_PARAM:
        return False, "אין כרגע מערכת רישום מחוברת"
    campaign = {k: referral[k] for k in ("source_type", "source_id", "headline",
                                         "source_url", "ctwa_clid") if referral.get(k)}
    payload = {
        "project": project, "project_name": proj["name"], "channel": "whatsapp",
        "name": name or phone, "phone": phone, "message": text,
        "campaign": campaign,
        "external_ref": f"{project}:{phone}",
    }
    try:
        code, body = post_json(TASK_URL, payload,
                               {TASK_TOKEN_HEADER: secret(TASK_TOKEN_PARAM)}, timeout=6)
        return 200 <= code < 300, f"{code} {body[:200]}"
    except urllib.error.HTTPError as e:
        return False, f"{e.code} {e.read().decode('utf-8', 'replace')[:200]}"
    except Exception as e:                      # noqa: BLE001 - never raise past here
        return False, f"{type(e).__name__}: {e}"


def to_telegram(proj: dict, name: str, phone: str, text: str, referral: dict,
                saved: bool, detail: str, returning: bool) -> bool:
    """Sent for every message: it is how a person learns a customer wrote."""
    if not saved:
        head = "🔴 וואטסאפ — הכתיבה ל-task-manager נכשלה"
    else:
        head = "💬 וואטסאפ — הודעה נוספת" if returning else "🟢 ליד חדש בוואטסאפ"
    lines = [f"{head} · {proj['name']}", f"שם: {name or '—'}", f"טלפון: {phone}",
             f"הודעה: {text}"]
    if referral.get("headline") or referral.get("source_url"):
        lines.append("מודעה: " + (referral.get("headline") or referral.get("source_url")))
    if not saved:
        lines.append(f"\n⚠️ שגיאת task-manager: {detail.strip()}\nהליד לא נשמר — טפל ידנית.")
    try:
        # Plain text, no parse_mode: Markdown chokes on "_" and drops the message.
        post_json(f"https://api.telegram.org/bot{secret(os.environ['TG_TOKEN_PARAM'])}/sendMessage",
                  {"chat_id": secret(os.environ["TG_CHAT_PARAM"]), "text": "\n".join(lines)},
                  {}, timeout=6)
        return True
    except Exception:                            # noqa: BLE001
        return False


def to_customer(wa_id: str, body: str) -> bool:
    try:
        post_json(f"{GRAPH}/{PHONE_ID}/messages",
                  {"messaging_product": "whatsapp", "to": wa_id, "type": "text",
                   "text": {"body": body}},
                  {"Authorization": f"Bearer {secret(os.environ['WA_TOKEN_PARAM'])}"}, timeout=8)
        return True
    except Exception as e:                       # noqa: BLE001
        detail = e.read().decode("utf-8", "replace")[:300] if hasattr(e, "read") else str(e)
        print(json.dumps({"level": "error", "reply_failed": detail}, ensure_ascii=False))
        return False


# ------------------------------------------------------------------ handler

def handle_message(msg: dict, names: dict):
    if not first_sight(msg.get("id", "")):
        return
    wa_id = msg.get("from", "")
    phone = local_phone(wa_id)
    name = names.get(wa_id, "")
    text = text_of(msg)[:1500]
    referral = msg.get("referral") or {}

    prior = contact(phone)
    project = campaign_of(text, referral, prior.get("project") or None)
    proj = CAMPAIGNS.get(project) or GENERAL
    slug = project or "general"

    saved, detail = to_task(slug, proj, name, phone, text, referral)
    told = to_telegram(proj, name, phone, text, referral, saved, detail,
                       returning=bool(prior))

    due = time.time() - int(prior.get("replied_at", 0)) > REPLY_GAP
    replied = due and to_customer(wa_id, proj["reply"])
    remember(phone, project, replied, prior)

    print(json.dumps({"level": "info" if saved else "error", "project": slug,
                      "task": detail, "telegram": told, "replied": bool(replied),
                      # the message itself only when nothing else kept it
                      **({} if saved else {"phone": phone, "name": name, "text": text})},
                     ensure_ascii=False))


def lambda_handler(event, _context):
    http = event.get("requestContext", {}).get("http", {})
    path = event.get("rawPath", "")
    # The path's last segment is the only credential a caller presents.
    key = path.rstrip("/").rsplit("/", 1)[-1]
    if not hmac.compare_digest(key, secret(os.environ["PATH_KEY_PARAM"])):
        return {"statusCode": 404, "body": ""}

    if http.get("method") == "GET":            # Meta's one-time subscription check
        q = event.get("queryStringParameters") or {}
        ok = (q.get("hub.mode") == "subscribe" and hmac.compare_digest(
            q.get("hub.verify_token", ""), secret(os.environ["VERIFY_TOKEN_PARAM"])))
        return {"statusCode": 200 if ok else 403, "body": q.get("hub.challenge", "") if ok else ""}

    try:
        body = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            import base64
            body = base64.b64decode(body).decode("utf-8")
        data = json.loads(body)
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value") or {}
                # Our WABA carries other numbers' traffic in principle; only
                # this line's messages are leads.
                if (value.get("metadata") or {}).get("phone_number_id") != PHONE_ID:
                    continue
                names = {c.get("wa_id"): (c.get("profile") or {}).get("name", "")
                         for c in value.get("contacts", [])}
                for msg in value.get("messages", []):     # statuses are ignored
                    try:
                        handle_message(msg, names)
                    except Exception as e:       # noqa: BLE001
                        # first_sight() already marked it handled, so Meta's
                        # retry will not bring it back: the log is its only copy.
                        print(json.dumps({"level": "error", "lost_message": msg,
                                          "why": f"{type(e).__name__}: {e}"},
                                         ensure_ascii=False))
    except Exception as e:                       # noqa: BLE001
        # Always 200: a non-200 makes Meta retry for hours and, repeated,
        # disable the webhook altogether.
        print(json.dumps({"level": "error", "unhandled": f"{type(e).__name__}: {e}"},
                         ensure_ascii=False))
    return {"statusCode": 200, "body": ""}
