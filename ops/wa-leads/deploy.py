# -*- coding: utf-8 -*-
"""
Deploys the shared WhatsApp lead line (handler.py).

    python deploy.py secrets     store the WhatsApp token + mint the path key in SSM
    python deploy.py deploy      table, role, function, HTTP API
    python deploy.py webhook     point Meta's webhook for our WABA at the function
    python deploy.py status      where Meta is sending messages right now

`webhook` is its own step on purpose: it is the moment the old bot stops
receiving messages, and it should never happen as a side effect of a deploy.

Same shape as bedek/ops/lead-proxy: plain aws CLI calls, stdlib + boto3 in the
function, no packaging step. It reuses that proxy's task-manager token and
Telegram parameters -- one system of record, one alert channel.
"""
import io, json, os, secrets as pysecrets, shutil, subprocess, sys, time, zipfile
import urllib.error, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNT = "824980746386"
REGION = "us-east-1"
FN = "tact-wa-leads"
ROLE = "tact-wa-leads-role"
API_NAME = "tact-wa-leads"
TABLE = "tact-wa-leads"

P_WA_TOKEN = "tact-wa-leads-whatsapp-token"
P_VERIFY = "tact-wa-leads-verify-token"
P_PATH_KEY = "tact-wa-leads-path-key"
# Owned by the lead proxy (bedek/ops/lead-proxy/deploy.py); read here, never written.
P_TASK = "yazam-il-task-manager-token"
P_TG_TOKEN = "yazam-il-telegram-token"
P_TG_CHAT = "yazam-il-telegram-chat"

TASK_URL = "https://task-manager.newavera.co.il/api/lead-intake"
# The line itself: 054-696-1875, WABA "bot ariel" under the business "Urban Whatsup".
WA_PHONE_ID_KEY = "WHATSAPP_PHONE_NUMBER_ID_ARIEL"
WA_TOKEN_KEY = "WHATSAPP_ACCESS_TOKEN_ARIEL"
WABA = "1410564280615182"
GRAPH = "https://graph.facebook.com/v21.0"

SHARED_ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")
AWS = shutil.which("aws") or "aws"       # on Windows it is aws.cmd


def aws(*args, parse=True, check=True):
    out = subprocess.run([AWS, *args], capture_output=True, text=True, encoding="utf-8",
                         env=dict(os.environ, AWS_PAGER="", PYTHONUTF8="1"))
    if check and out.returncode:
        raise SystemExit(f"aws {' '.join(args[:3])} failed:\n{out.stderr.strip()}")
    if out.returncode:
        return None
    return json.loads(out.stdout) if parse and out.stdout.strip() else out.stdout.strip()


def env_value(key):
    # Parsed, not grepped: the shared .env has no trailing newline.
    for line in io.open(SHARED_ENV, encoding="utf-8", errors="replace").read().splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{key} not in the shared .env")


def param(name):
    return aws("ssm", "get-parameter", "--region", REGION, "--name", name, "--with-decryption",
               "--query", "Parameter.Value", "--output", "text", parse=False, check=False)


def graph(method, path, data=None):
    url = f"{GRAPH}/{path}"
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method,
                                 headers={"Authorization": f"Bearer {env_value(WA_TOKEN_KEY)}"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        return json.load(e)


# ------------------------------------------------------------------ secrets

def put_secrets():
    def put(name, value):
        aws("ssm", "put-parameter", "--region", REGION, "--name", name, "--type",
            "SecureString", "--overwrite", "--value", value, parse=False)
        print(f"   {name}")

    put(P_WA_TOKEN, env_value(WA_TOKEN_KEY))
    # Minted once and kept: rotating either would silently unhook the webhook.
    for name in (P_VERIFY, P_PATH_KEY):
        if param(name):
            print(f"   {name} (kept)")
        else:
            put(name, pysecrets.token_urlsafe(32))


# --------------------------------------------------------------------- infra

TRUST = json.dumps({"Version": "2012-10-17", "Statement": [{
    "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"}]})


def ensure_table():
    if aws("dynamodb", "describe-table", "--region", REGION, "--table-name", TABLE,
           parse=False, check=False):
        return
    aws("dynamodb", "create-table", "--region", REGION, "--table-name", TABLE,
        "--attribute-definitions", "AttributeName=pk,AttributeType=S",
        "--key-schema", "AttributeName=pk,KeyType=HASH",
        "--billing-mode", "PAY_PER_REQUEST", parse=False)
    aws("dynamodb", "wait", "table-exists", "--region", REGION, "--table-name", TABLE, parse=False)
    # Seen-message markers expire; contacts carry no ttl and stay.
    aws("dynamodb", "update-time-to-live", "--region", REGION, "--table-name", TABLE,
        "--time-to-live-specification", "Enabled=true,AttributeName=ttl", parse=False)
    print(f"   table {TABLE} created")


def ensure_role():
    arn = aws("iam", "get-role", "--role-name", ROLE, "--query", "Role.Arn",
              "--output", "text", parse=False, check=False)
    fresh = not arn
    if fresh:
        arn = aws("iam", "create-role", "--role-name", ROLE,
                  "--assume-role-policy-document", TRUST,
                  "--query", "Role.Arn", "--output", "text", parse=False)
        aws("iam", "attach-role-policy", "--role-name", ROLE, "--policy-arn",
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", parse=False)
    # Re-applied on every deploy: a parameter added later is otherwise a silent
    # AccessDenied inside the function.
    aws("iam", "put-role-policy", "--role-name", ROLE, "--policy-name", "own-secrets-and-table",
        "--policy-document", json.dumps({"Version": "2012-10-17", "Statement": [
            {"Effect": "Allow", "Action": ["ssm:GetParameter"],
             "Resource": [f"arn:aws:ssm:{REGION}:{ACCOUNT}:parameter/{p}" for p in
                          (P_WA_TOKEN, P_VERIFY, P_PATH_KEY, P_TASK, P_TG_TOKEN, P_TG_CHAT)]},
            {"Effect": "Allow", "Action": ["dynamodb:GetItem", "dynamodb:PutItem"],
             "Resource": f"arn:aws:dynamodb:{REGION}:{ACCOUNT}:table/{TABLE}"},
        ]}), parse=False)
    if fresh:
        print(f"   role {ROLE} created; waiting for IAM to propagate")
        time.sleep(12)
    return arn


def ensure_function(role):
    zip_path = os.path.join(HERE, "function.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(HERE, "handler.py"), "handler.py")
    # The WHOLE environment: update-function-configuration replaces it.
    env = json.dumps({"Variables": {
        "TASK_URL": TASK_URL, "TASK_TOKEN_PARAM": P_TASK, "TASK_TOKEN_HEADER": "X-Lead-Token",
        "TG_TOKEN_PARAM": P_TG_TOKEN, "TG_CHAT_PARAM": P_TG_CHAT,
        "WA_TOKEN_PARAM": P_WA_TOKEN, "WA_PHONE_ID": env_value(WA_PHONE_ID_KEY),
        "VERIFY_TOKEN_PARAM": P_VERIFY, "PATH_KEY_PARAM": P_PATH_KEY, "TABLE": TABLE}})
    common = ("--timeout", "25", "--memory-size", "256", "--environment", env)
    if aws("lambda", "get-function", "--region", REGION, "--function-name", FN,
           parse=False, check=False):
        aws("lambda", "update-function-code", "--region", REGION, "--function-name", FN,
            "--zip-file", f"fileb://{zip_path}", parse=False)
        aws("lambda", "wait", "function-updated", "--region", REGION, "--function-name", FN, parse=False)
        aws("lambda", "update-function-configuration", "--region", REGION,
            "--function-name", FN, *common, parse=False)
        aws("lambda", "wait", "function-updated", "--region", REGION, "--function-name", FN, parse=False)
        print("   function updated")
    else:
        aws("lambda", "create-function", "--region", REGION, "--function-name", FN,
            "--runtime", "python3.13", "--role", role, "--handler", "handler.lambda_handler",
            "--zip-file", f"fileb://{zip_path}", *common, parse=False)
        aws("lambda", "wait", "function-active", "--region", REGION, "--function-name", FN, parse=False)
        print("   function created")
    os.remove(zip_path)
    return f"arn:aws:lambda:{REGION}:{ACCOUNT}:function:{FN}"


def ensure_api(fn_arn):
    """HTTP API in front of the function. Not a function URL: public ones are
    blocked in this account (bedek/ops/leads.md)."""
    apis = aws("apigatewayv2", "get-apis", "--region", REGION)["Items"]
    api = next((a for a in apis if a["Name"] == API_NAME), None)
    if not api:
        api = aws("apigatewayv2", "create-api", "--region", REGION, "--name", API_NAME,
                  "--protocol-type", "HTTP", "--target", fn_arn)
        aws("lambda", "add-permission", "--region", REGION, "--function-name", FN,
            "--statement-id", "apigw-invoke", "--action", "lambda:InvokeFunction",
            "--principal", "apigateway.amazonaws.com", "--source-arn",
            f"arn:aws:execute-api:{REGION}:{ACCOUNT}:{api['ApiId']}/*", parse=False)
        print(f"   api {API_NAME} created")
    return api["ApiEndpoint"]


def endpoint():
    apis = aws("apigatewayv2", "get-apis", "--region", REGION)["Items"]
    api = next((a for a in apis if a["Name"] == API_NAME), None)
    if not api:
        raise SystemExit("not deployed yet -- run `python deploy.py deploy`")
    return api["ApiEndpoint"]


def deploy():
    for p in (P_WA_TOKEN, P_VERIFY, P_PATH_KEY, P_TASK, P_TG_TOKEN, P_TG_CHAT):
        if not param(p):
            raise SystemExit(f"SSM parameter {p} missing -- run `python deploy.py secrets`")
    ensure_table()
    fn_arn = ensure_function(ensure_role())
    base = ensure_api(fn_arn)
    # Check the door itself, not the exit codes: a wrong key must be refused,
    # and Meta's handshake must get its challenge back.
    def get(url):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, ""
    time.sleep(3)
    print("   wrong key   ->", get(f"{base}/wa/not-the-key")[0], "(want 404)")
    q = urllib.parse.urlencode({"hub.mode": "subscribe", "hub.challenge": "ping-123",
                                "hub.verify_token": param(P_VERIFY)})
    print("   handshake   ->", get(f"{base}/wa/{param(P_PATH_KEY)}?{q}"), "(want 200, ping-123)")


# -------------------------------------------------------------------- webhook

def status():
    for app in graph("GET", f"{WABA}/subscribed_apps").get("data", []):
        d = app.get("whatsapp_business_api_data", {})
        over = app.get("override_callback_uri") or "(app default)"
        # never print the path key
        print(f"   app {d.get('name')} {d.get('id')} -> {over.rsplit('/', 1)[0]}/…")


def webhook():
    url = f"{endpoint()}/wa/{param(P_PATH_KEY)}"
    r = graph("POST", f"{WABA}/subscribed_apps",
              {"override_callback_uri": url, "verify_token": param(P_VERIFY)})
    print("   subscribe:", r)
    status()


if __name__ == "__main__":
    {"secrets": put_secrets, "deploy": deploy, "webhook": webhook, "status": status}[
        sys.argv[1] if len(sys.argv) > 1 else "status"]()
