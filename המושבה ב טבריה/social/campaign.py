# -*- coding: utf-8 -*-
"""
The Meta campaign for המושבה ב׳, built from the approved material in SharePoint.

    python campaign.py plan        show what would be built, change nothing
    python campaign.py build       create campaign, ad set and ads -- all PAUSED
    python campaign.py apply       push ADSET name / targeting / budget / end date to the live ad set
    python campaign.py status      what exists and what state it is in
    python campaign.py activate    turn it on (spends money)
    python campaign.py pause       turn it off

`build` never spends: everything is created paused, and `activate` is a
separate command on purpose. Re-running `build` reuses what exists by name.

Ad text and images are read from SharePoint at build time, not copied here:
the approved wording lives in one place, and a copy in the repo would be the
one that missed the last correction.
"""
import base64, json, os, re, sys, urllib.error, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "bedek", "ops")))
from sharepoint import Graph, env  # noqa: E402

GRAPH = "https://graph.facebook.com/v21.0"
ACCOUNT = "act_1501272988689802"     # "TACT NIRIM" -- the portfolio's only ad account
PAGE = "1340214009171909"            # טבריה - המושבה ב
PIXEL = "28613934514923512"          # moshava-b
SITE = "https://moshava-b.newavera.co.il/"
SP = "TACT/שיווק/מכירת קרקע בטבריה/רשתות"

CAMPAIGN = "המושבה ב׳ | תנועה לדף | צפון"
ADSET = "טבריה 25 ק״מ | 18-65 | פייסבוק"
DAILY_BUDGET_ILS = 30
RUN_DAYS = 30                    # the ad set stops itself; nobody has to remember
# Landing-page views, not leads: at this budget, with a pixel that has never
# seen a Lead, a leads objective has nothing to learn from and barely serves.
# Switch to OUTCOME_LEADS + the pixel's Lead event when the budget goes up.
OBJECTIVE, GOAL = "OUTCOME_TRAFFIC", "LANDING_PAGE_VIEWS"

# (name, image in SharePoint, heading of the approved text in the .md, headline)
ADS = [
    ("ad1 | השקה | כנרת", "מודעות מאושרות/ad1-launch-kinneret-FINAL.png",
     "מודעה 1", "זכות בקרקע במחיר השקה"),
    ("ad3 | הבית הבא | פוריה", "מודעות מאושרות/ad3-buyers-poria-FINAL.png",
     "מודעה 3", "הבית הבא שלך – בראייה עתידית"),
]
TEXTS_MD = "facebook-ads-text-only-approved.md"
DESCRIPTION = "המושבה ב׳ · רכס פוריה · טבריה"

TARGETING = {
    # 25km around Tiberias (Boaz, 2026-10-05). The circle crosses the Yarmouk
    # into Jordan and brushes Syria, hence the exclusion: without it part of a
    # 30-shekel day is spent showing Hebrew ads across the border.
    "geo_locations": {"cities": [{"key": "1015197", "radius": 25, "distance_unit": "kilometer"}],
                      "location_types": ["home", "recent"]},
    "excluded_geo_locations": {"countries": ["JO", "SY"]},
    # 18-65+ with no gender or interest filter is all the Housing category allows.
    "age_min": 18, "age_max": 65,
    "targeting_automation": {"advantage_audience": 0},
    # Facebook only until the page has an Instagram account to answer from.
    "publisher_platforms": ["facebook"],
}

TOKEN = env("META_PAGE_TOKEN_BEDEK")     # Tact publisher -- ads_management


def api(method, path, **params):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
            for k, v in params.items()}
    data["access_token"] = TOKEN
    url = f"{GRAPH}/{path}"
    if method == "GET":
        url, body = url + "?" + urllib.parse.urlencode(data), None
    else:
        body = urllib.parse.urlencode(data).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=body, method=method),
                                    timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        err = json.load(e).get("error", {})
        raise SystemExit(f"Meta refused {method} {path}:\n  {err.get('message')}\n  "
                         f"{err.get('error_user_title', '')} {err.get('error_user_msg', '')}")


def by_name(edge, name, fields="id,name,status,effective_status"):
    rows = api("GET", f"{ACCOUNT}/{edge}", fields=fields, limit=200).get("data", [])
    return next((r for r in rows if r["name"] == name), None)


# ------------------------------------------------------------- SharePoint

def sharepoint_bytes(g, rel):
    url = g.drive(f"{SP}/{rel}") + ":/content"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {g.t}"})
    return urllib.request.urlopen(req, timeout=120).read()


def approved_text(md, heading):
    """The body under '## <heading> — …', up to the next rule."""
    m = re.search(rf"^## {re.escape(heading)}\b[^\n]*\n(.*?)(?=^---|\Z)", md, re.S | re.M)
    if not m:
        raise SystemExit(f"'{heading}' not found in {TEXTS_MD}")
    return m.group(1).strip()


def material():
    g = Graph()
    md = sharepoint_bytes(g, TEXTS_MD).decode("utf-8")
    return [(name, sharepoint_bytes(g, img), approved_text(md, heading), headline, img)
            for name, img, heading, headline in ADS]


# ------------------------------------------------------------------ steps

def plan():
    print(f"חשבון   {ACCOUNT}\nקמפיין  {CAMPAIGN}  [{OBJECTIVE} → {GOAL}, קטגוריה: HOUSING]")
    print(f"קבוצה   {ADSET}  ·  {DAILY_BUDGET_ILS} ₪ ליום\nיעד     {SITE}\n")
    for name, img, text, headline, rel in material():
        print(f"── {name}   ({rel}, {len(img) // 1024}KB)\nכותרת: {headline}\n{text}\n")


def build():
    c = by_name("campaigns", CAMPAIGN)
    if not c:
        c = api("POST", f"{ACCOUNT}/campaigns", name=CAMPAIGN, objective=OBJECTIVE,
                status="PAUSED", special_ad_categories=["HOUSING"],
                special_ad_category_country=["IL"], is_adset_budget_sharing_enabled="false")
        print("campaign created", c["id"])
    existing = api("GET", f"{c['id']}/adsets", fields="id,name").get("data", [])
    s = existing[0] if existing else None
    if not s:
        s = api("POST", f"{ACCOUNT}/adsets", name=ADSET, campaign_id=c["id"],
                daily_budget=DAILY_BUDGET_ILS * 100,        # in agorot
                billing_event="IMPRESSIONS", optimization_goal=GOAL,
                bid_strategy="LOWEST_COST_WITHOUT_CAP", destination_type="WEBSITE",
                targeting=TARGETING, status="PAUSED")
        print("ad set created", s["id"])
    for name, img, text, headline, _rel in material():
        if by_name("ads", name):
            print("ad exists", name)
            continue
        h = api("POST", f"{ACCOUNT}/adimages", bytes=base64.b64encode(img).decode())
        image_hash = next(iter(h["images"].values()))["hash"]
        creative = api("POST", f"{ACCOUNT}/adcreatives", name=name, object_story_spec={
            "page_id": PAGE,
            "link_data": {"link": SITE, "message": text, "name": headline,
                          "description": DESCRIPTION, "image_hash": image_hash,
                          "call_to_action": {"type": "LEARN_MORE", "value": {"link": SITE}}}},
            # How the lead proxy and task-manager learn which ad a lead came from.
            url_tags="utm_source=facebook&utm_medium=paid&utm_campaign=north-traffic"
                     f"&utm_content={name.split(' ')[0]}")
        ad = api("POST", f"{ACCOUNT}/ads", name=name, adset_id=s["id"],
                 creative={"creative_id": creative["id"]}, status="PAUSED",
                 tracking_specs=[{"action.type": ["offsite_conversion"], "fb_pixel": [PIXEL]}])
        print("ad created", name, ad["id"])
    status()


def apply():
    """Bring the live ad set in line with the settings above. The ad set is
    found through the campaign, not by name, so renaming it here renames it
    there instead of building a second one."""
    c = by_name("campaigns", CAMPAIGN)
    if not c:
        raise SystemExit("not built yet")
    s = api("GET", f"{c['id']}/adsets", fields="id,name,start_time").get("data", [])[0]
    from datetime import datetime, timedelta
    end = datetime.fromisoformat(s["start_time"].replace("+0000", "+00:00")) + timedelta(days=RUN_DAYS)
    api("POST", s["id"], name=ADSET, targeting=TARGETING,
        daily_budget=DAILY_BUDGET_ILS * 100, end_time=end.isoformat())
    status()


def status():
    c = by_name("campaigns", CAMPAIGN, "id,name,status,effective_status,objective,special_ad_categories")
    if not c:
        return print("not built yet")
    print(f"\nקמפיין  {c['name']}  {c['effective_status']}  {c['objective']} {c['special_ad_categories']}")
    for s in api("GET", f"{c['id']}/adsets",
                 fields="name,effective_status,daily_budget,optimization_goal,start_time,"
                        "end_time,targeting").get("data", []):
        geo = s["targeting"].get("geo_locations", {})
        where = ", ".join(f"{x['name']} +{x.get('radius')}{'km' if x.get('distance_unit') == 'kilometer' else 'mi'}"
                          for x in geo.get("cities", [])) or json.dumps(geo, ensure_ascii=False)
        print(f"קבוצה   {s['name']}  {s['effective_status']}  "
              f"{int(s['daily_budget']) / 100:.0f} ₪/יום  {s['optimization_goal']}")
        print(f"        {where}  ·  ללא {s['targeting'].get('excluded_geo_locations', {}).get('countries', '—')}"
              f"  ·  {s.get('start_time', '')[:10]} → {s.get('end_time', 'ללא תאריך סיום')[:10]}")
    for a in api("GET", f"{c['id']}/ads",
                 fields="id,name,effective_status,issues_info,ad_review_feedback").get("data", []):
        print(f"מודעה   {a['name']}  {a['effective_status']}  {a['id']}")
        for i in a.get("issues_info", []):
            print(f"        ⚠ {i.get('error_summary')}: {i.get('error_message')}")
        if a.get("ad_review_feedback"):
            print(f"        ⚠ review: {a['ad_review_feedback']}")


def switch(state):
    c = by_name("campaigns", CAMPAIGN)
    if not c:
        raise SystemExit("not built yet")
    # Campaign, ad set and ads each carry their own switch; all three must agree.
    for edge in ("ads", "adsets"):
        for row in api("GET", f"{c['id']}/{edge}", fields="id").get("data", []):
            api("POST", row["id"], status=state)
    api("POST", c["id"], status=state)
    status()


if __name__ == "__main__":
    {"plan": plan, "build": build, "apply": apply, "status": status,
     "activate": lambda: switch("ACTIVE"), "pause": lambda: switch("PAUSED")}[
        sys.argv[1] if len(sys.argv) > 1 else "status"]()
