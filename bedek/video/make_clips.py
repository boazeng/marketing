# -*- coding: utf-8 -*-
"""
Live-action B-roll from fal.ai.

Model: Wan 2.2 turbo, which bills **$0.10 per clip, not per second** -- the
distinction that decides the whole budget. Ten clips is one dollar; the same
footage on a per-second model would be closer to eight.

All jobs are submitted first and polled afterwards, so ten clips take about as
long as one. Every clip is cached by filename: re-running only regenerates what
is missing, so a retake of one shot costs ten cents rather than a dollar.

    python make_clips.py             everything missing
    python make_clips.py a4 b2       just those beats (delete the mp4 first
                                     to force a retake)
"""
import io, json, os, sys, time, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scripts import LOOK, VIDEOS  # noqa: E402

OUT = os.path.join(HERE, "clips")
ENDPOINT = "fal-ai/wan/v2.2-a14b/text-to-video/turbo"
PRICE = 0.10
# The shared secrets file. Override with TACT_ENV on a machine where it
# lives elsewhere -- nothing in this repo may ever contain a secret.
ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")


def env(key):
    for raw in io.open(ENV, encoding="utf-8", errors="replace").read().splitlines():
        l = raw.strip().lstrip("\ufeff")
        if l.startswith(key + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{key} not in the shared .env")


KEY = env("FALAI_API_KEY")
H = {"Authorization": f"Key {KEY}", "Content-Type": "application/json"}


def api(url, body=None):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode() if body else None,
        headers=H, method="POST" if body else "GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode("utf-8", "replace")[:400]}


def submit(prompt):
    return api(f"https://queue.fal.run/{ENDPOINT}", {
        "prompt": prompt,
        "resolution": "720p",
        "aspect_ratio": "16:9",
        "video_quality": "high",
        "acceleration": "regular",
        # The prompts are already specific; letting an LLM expand them tends to
        # add the on-screen text and logos the prompt explicitly forbids.
        "enable_prompt_expansion": False,
    })


def download(url, path):
    with urllib.request.urlopen(url, timeout=180) as r:
        io.open(path, "wb").write(r.read())


if __name__ == "__main__":
    want = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)

    todo = []
    for v in VIDEOS:
        for b in v["beats"]:
            if b.get("card"):
                continue
            if want and b["id"] not in want:
                continue
            path = os.path.join(OUT, f"{v['slug']}-{b['id']}.mp4")
            if os.path.exists(path):
                print(f"  cached  {b['id']}")
                continue
            todo.append((v["slug"], b, path))

    if not todo:
        print("nothing to generate.")
        sys.exit(0)

    print(f"\nsubmitting {len(todo)} clips  ~${len(todo) * PRICE:.2f}\n")
    jobs = []
    for slug, b, path in todo:
        r = submit(f"{b['visual']} {LOOK}")
        if "_error" in r:
            print(f"  {b['id']} SUBMIT FAILED {r['_error']}: {r['_body']}")
            continue
        jobs.append({"id": b["id"], "path": path,
                     "status_url": r["status_url"], "response_url": r["response_url"]})
        print(f"  queued  {b['id']}")

    print("\npolling...")
    pending = {j["id"]: j for j in jobs}
    spent = 0.0
    for attempt in range(90):
        for jid in list(pending):
            j = pending[jid]
            st = api(j["status_url"])
            status = st.get("status")
            if status == "COMPLETED":
                res = api(j["response_url"])
                url = (res.get("video") or {}).get("url")
                if url:
                    download(url, j["path"])
                    spent += PRICE
                    print(f"  done    {jid}  -> {os.path.basename(j['path'])}")
                else:
                    print(f"  {jid} completed but no video: {json.dumps(res)[:200]}")
                del pending[jid]
            elif status in ("FAILED", "ERROR"):
                print(f"  FAILED  {jid}: {json.dumps(st)[:200]}")
                del pending[jid]
        if not pending:
            break
        time.sleep(10)

    if pending:
        print(f"\nstill running after 15 min: {', '.join(pending)}")
    print(f"\nspent this run: ~${spent:.2f}")
