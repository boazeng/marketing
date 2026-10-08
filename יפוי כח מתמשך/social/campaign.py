# -*- coding: utf-8 -*-
"""
Builds the Facebook campaign from the approved ads in ads.py.

    python campaign.py build       create everything PAUSED -- spends nothing
    python campaign.py status      what exists, its review state, spend so far
    python campaign.py activate    start: 30 days from now, then switch on
    python campaign.py pause       stop spending, keep everything

Nothing here spends money except `activate`, and that one is run only on
Boaz's say-so.

The settings below are his (2026-10-05): clicks to the landing page, Hod
HaSharon + Kfar Saba, age 40+, 20 ILS a day, 30 days, Facebook only.
"""
import io, json, os, sys, time, urllib.error, urllib.parse, urllib.request, uuid

sys.stdout.reconfigure(encoding="utf-8")

from ads import ADS, CTA, URL
from assets import OUT
from upload_assets import API, PAGE_ID, SYSTEM_TOKEN, env

ACCOUNT = "act_1501272988689802"     # TACT NIRIM -- shared with טבריה
PIXEL = "1531044362163696"           # zohar-poa, on the landing page

# The account is shared: the project prefix is what splits the spend report.
CAMPAIGN = "ייפוי כוח | תנועה לדף | הוד השרון וכפר סבא"
ADSET = "ייפוי כוח | 40+ | הוד השרון וכפר סבא | פייסבוק"
DAILY_BUDGET = 2000                  # agorot -> 20 ILS
DAYS = 30

# Which render goes to which Facebook placement (ads.py FORMATS). Meta would
# otherwise crop one image for all of them, and a crop of a text image cuts text.
PLACEMENTS = {
    "4x5":     ["feed", "profile_feed"],
    "1x1":     ["marketplace", "search"],
    "9x16":    ["story", "facebook_reels"],
    "191x100": ["right_hand_column"],
}

TARGETING = {
    "geo_locations": {
        "cities": [{"key": "1013378"}, {"key": "1013784"}],   # Hod HaSharon, Kfar Saba
        "location_types": ["home", "recent"],
    },
    "age_min": 40,
    "publisher_platforms": ["facebook"],
    "facebook_positions": [p for ps in PLACEMENTS.values() for p in ps],
    # Off on purpose: with it on, Meta treats the age floor as a suggestion.
    "targeting_automation": {"advantage_audience": 0},
}

TOKEN = env(SYSTEM_TOKEN)


def call(path, fields=None, method="GET", file=None):
    fields = {k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
              for k, v in (fields or {}).items()}
    fields["access_token"] = TOKEN
    url, data, headers = API + path, None, {}
    if method == "GET":
        url += "?" + urllib.parse.urlencode(fields)
    elif file:
        b = uuid.uuid4().hex
        parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
                 for k, v in fields.items()]
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="filename"; '
                     f'filename="{os.path.basename(file)}"\r\nContent-Type: image/png\r\n\r\n'.encode()
                     + io.open(file, "rb").read() + b"\r\n")
        data = b"".join(parts) + f"--{b}--\r\n".encode()
        headers["Content-Type"] = f"multipart/form-data; boundary={b}"
    else:
        data = urllib.parse.urlencode(fields).encode()
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        return json.loads(urllib.request.urlopen(r, timeout=120).read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read()).get("error", {})
        raise SystemExit(f"{method} {path}: {e.code} {err.get('message')}\n"
                         f"   {err.get('error_user_title') or ''} {err.get('error_user_msg') or ''}")


def find(edge, name, fields="id,name,status,effective_status"):
    rows = call(f"{ACCOUNT}/{edge}", {"fields": fields, "limit": 200})["data"]
    return next((r for r in rows if r["name"] == name), None)


def creative_spec(n, ad):
    """One ad, four images, each pinned to the placements it was drawn for."""
    images, rules = [], []
    for fmt, positions in PLACEMENTS.items():
        path = os.path.join(OUT, f"ad-{n}-{fmt}.png")
        h = next(iter(call(f"{ACCOUNT}/adimages", {}, "POST", path)["images"].values()))["hash"]
        images.append({"hash": h, "adlabels": [{"name": fmt}]})
        rules.append({"customization_spec": {"publisher_platforms": ["facebook"],
                                             "facebook_positions": positions},
                      "image_label": {"name": fmt}, "body_label": {"name": "body"},
                      "title_label": {"name": "title"}, "link_url_label": {"name": "link"}})
    return {
        "images": images,
        "bodies": [{"text": ad["primary"], "adlabels": [{"name": "body"}]}],
        "titles": [{"text": ad["headline"], "adlabels": [{"name": "title"}]}],
        "link_urls": [{"website_url": URL, "adlabels": [{"name": "link"}]}],
        "call_to_action_types": [CTA],
        "ad_formats": ["SINGLE_IMAGE"],
        "asset_customization_rules": rules,
    }


def build():
    """Find-or-create at every level, so a run that died halfway is finished
    by running it again -- never by a second campaign that also spends."""
    camp = find("campaigns", CAMPAIGN) or call(f"{ACCOUNT}/campaigns", {
        "name": CAMPAIGN, "objective": "OUTCOME_TRAFFIC", "status": "PAUSED",
        "special_ad_categories": [],
        # Required whenever the budget sits on the ad set. One ad set, nothing to share.
        "is_adset_budget_sharing_enabled": "false"}, "POST")
    print(f"   campaign {camp['id']}")
    now = int(time.time())
    adset = find("adsets", ADSET) or call(f"{ACCOUNT}/adsets", {
        "name": ADSET, "campaign_id": camp["id"], "status": "PAUSED",
        "daily_budget": DAILY_BUDGET, "billing_event": "IMPRESSIONS",
        "optimization_goal": "LINK_CLICKS", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "destination_type": "WEBSITE", "targeting": TARGETING,
        # Placeholder dates: `activate` resets them so the 30 days start at launch.
        "start_time": now + 3600, "end_time": now + 3600 + DAYS * 86400}, "POST")
    print(f"   ad set   {adset['id']}")
    for n, ad in enumerate(ADS, 1):
        name = f"ייפוי כוח | {n} | {ad['key']}"
        if find("ads", name):
            print(f"   ad {n}     exists  {ad['key']}")
            continue
        creative = call(f"{ACCOUNT}/adcreatives", {
            "name": name, "object_story_spec": {"page_id": PAGE_ID},
            "asset_feed_spec": creative_spec(n, ad),
            "url_tags": f"utm_source=facebook&utm_medium=paid&utm_campaign=poa-traffic&utm_content={ad['key']}",
        }, "POST")["id"]
        a = call(f"{ACCOUNT}/ads", {
            "name": name, "adset_id": adset["id"], "creative": {"creative_id": creative},
            "status": "PAUSED",
            "tracking_specs": [{"action.type": ["offsite_conversion"], "fb_pixel": [PIXEL]}],
        }, "POST")["id"]
        print(f"   ad {n}     {a}  {ad['key']}")
    status()


def tree():
    camp = find("campaigns", CAMPAIGN)
    if not camp:
        raise SystemExit("no campaign yet -- run `build`")
    adsets = call(f"{camp['id']}/adsets", {"fields": "id,name,status,effective_status,"
                  "daily_budget,start_time,end_time,targeting"})["data"]
    ads = call(f"{camp['id']}/ads", {"fields": "id,name,status,effective_status,"
               "ad_review_feedback,issues_info"})["data"]
    return camp, adsets, ads


def status():
    camp, adsets, ads = tree()
    print(f"\n{camp['name']}\n   {camp['effective_status']}")
    for s in adsets:
        t = s["targeting"]
        print(f"   {s['name']}\n      {s['effective_status']} · {int(s['daily_budget'])/100:.0f} ILS/day · "
              f"{s['start_time'][:10]} -> {s.get('end_time', '')[:10]} · age {t.get('age_min')}+ · "
              f"{t.get('publisher_platforms')} · {[c['name'] for c in t['geo_locations']['cities']]}")
    for a in sorted(ads, key=lambda a: a["name"]):
        note = a.get("ad_review_feedback") or a.get("issues_info") or ""
        print(f"      {a['effective_status']:16} {a['name']}  {json.dumps(note, ensure_ascii=False) if note else ''}")
    ins = call(f"{camp['id']}/insights", {"fields": "spend,impressions,inline_link_clicks",
                                          "date_preset": "maximum"})["data"]
    print(f"   spend so far: {ins[0] if ins else 'none'}")


def switch(state):
    camp, adsets, ads = tree()
    if state == "ACTIVE":
        now = int(time.time())
        for s in adsets:
            call(s["id"], {"start_time": now, "end_time": now + DAYS * 86400}, "POST")
    for o in [camp] + adsets + ads:
        call(o["id"], {"status": state}, "POST")
    status()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"build": build, "status": status, "activate": lambda: switch("ACTIVE"),
     "pause": lambda: switch("PAUSED")}[cmd]()
