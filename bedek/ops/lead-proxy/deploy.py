# -*- coding: utf-8 -*-
"""
Deploys the lead proxy: IAM role, Lambda, SSM parameters.

    python deploy.py secrets     store/refresh the three secrets in SSM
    python deploy.py deploy      create or update the function
    python deploy.py test        send a synthetic lead through the live CDN

Plain boto3-free CLI calls so this needs nothing installed beyond the aws CLI
that is already on this machine. The function itself is stdlib + boto3 (which
the Lambda runtime provides), so there is no packaging step and no Docker --
same reasoning as the CRM's own Lambda.
"""
import io, json, os, shutil, subprocess, sys, time, zipfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNT = "824980746386"
REGION = "us-east-1"
FN = "yazam-il-lead-proxy"
ROLE = "yazam-il-lead-proxy-role"
P_CRM = "yazam-il-crm-api-key"
P_TG_TOKEN = "yazam-il-telegram-token"
P_TG_CHAT = "yazam-il-telegram-chat"
# The shared secrets file. Override with TACT_ENV on a machine where it
# lives elsewhere -- nothing in this repo may ever contain a secret.
SHARED_ENV = os.environ.get("TACT_ENV", r"C:\Users\User\Aiprojects\env\.env")

AWS = shutil.which("aws") or "aws"


def aws(*args, parse=True, check=True):
    out = subprocess.run([AWS, *args], capture_output=True, text=True,
                         env=dict(os.environ, AWS_PAGER=""))
    if check and out.returncode:
        raise SystemExit(f"aws {' '.join(args[:3])} failed:\n{out.stderr.strip()}")
    if out.returncode:
        return None
    return json.loads(out.stdout) if parse and out.stdout.strip() else out.stdout.strip()


def env_value(key):
    for line in io.open(SHARED_ENV, encoding="utf-8", errors="replace"):
        if line.startswith(key + "="):
            # quoted because a value may contain '#', which otherwise truncates
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


# ------------------------------------------------------------------ secrets

def put_secrets():
    tg_token = env_value("TELEGRAM_BOT_TOKEN")
    tg_chat = env_value("RAN_TELEGRAM_CHAT_ID")
    if not tg_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN not found in the shared .env")

    for name, value in ((P_TG_TOKEN, tg_token), (P_TG_CHAT, tg_chat)):
        if not value:
            print(f"   skipped {name} (no value)")
            continue
        aws("ssm", "put-parameter", "--region", REGION, "--name", name,
            "--type", "SecureString", "--overwrite", "--value", value, parse=False)
        print(f"   {name}")

    key = os.environ.get("CRM_API_KEY")
    if key:
        aws("ssm", "put-parameter", "--region", REGION, "--name", P_CRM,
            "--type", "SecureString", "--overwrite", "--value", key, parse=False)
        print(f"   {P_CRM}")
    else:
        print(f"\n   {P_CRM} NOT set -- create an API key in TACT-CRM")
        print("   (ניהול חברה -> מפתחות API), then run:")
        print(f'     CRM_API_KEY=<key> python deploy.py secrets')


# --------------------------------------------------------------------- role

TRUST = json.dumps({
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"},
                   "Action": "sts:AssumeRole"}],
})


def ensure_role():
    existing = aws("iam", "get-role", "--role-name", ROLE,
                   "--query", "Role.Arn", "--output", "text", parse=False, check=False)
    if existing:
        return existing

    arn = aws("iam", "create-role", "--role-name", ROLE,
              "--assume-role-policy-document", TRUST,
              "--query", "Role.Arn", "--output", "text", parse=False)
    aws("iam", "attach-role-policy", "--role-name", ROLE, "--policy-arn",
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", parse=False)
    # Read exactly these three parameters and nothing else.
    aws("iam", "put-role-policy", "--role-name", ROLE, "--policy-name", "read-own-secrets",
        "--policy-document", json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["ssm:GetParameter"],
                "Resource": [f"arn:aws:ssm:{REGION}:{ACCOUNT}:parameter/{p}"
                             for p in (P_CRM, P_TG_TOKEN, P_TG_CHAT,
                                       "yazam-il-edge-secret")],
            }],
        }), parse=False)
    print(f"   role {ROLE} created; waiting for IAM to propagate")
    time.sleep(12)          # a fresh role is not immediately assumable
    return arn


# ------------------------------------------------------------------- deploy

def package():
    path = os.path.join(HERE, "function.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(HERE, "handler.py"), "handler.py")
    return path


ENV = {"Variables": {
    "CRM_URL": "https://crm-db.newavera.co.il/api/v1/customers",
    "CRM_KEY_PARAM": P_CRM,
    "TG_TOKEN_PARAM": P_TG_TOKEN,
    "TG_CHAT_PARAM": P_TG_CHAT,
}}


def deploy():
    role = ensure_role()
    zip_path = package()

    exists = aws("lambda", "get-function", "--region", REGION, "--function-name", FN,
                 parse=False, check=False)
    if exists:
        aws("lambda", "update-function-code", "--region", REGION, "--function-name", FN,
            "--zip-file", f"fileb://{zip_path}", parse=False)
        aws("lambda", "wait", "function-updated", "--region", REGION,
            "--function-name", FN, parse=False)
        aws("lambda", "update-function-configuration", "--region", REGION,
            "--function-name", FN, "--environment", json.dumps(ENV),
            "--timeout", "20", "--memory-size", "256", parse=False)
        print("   function updated")
    else:
        aws("lambda", "create-function", "--region", REGION, "--function-name", FN,
            "--runtime", "python3.13", "--role", role, "--handler", "handler.lambda_handler",
            "--zip-file", f"fileb://{zip_path}", "--timeout", "20", "--memory-size", "256",
            "--environment", json.dumps(ENV), parse=False)
        aws("lambda", "wait", "function-active", "--region", REGION,
            "--function-name", FN, parse=False)
        print("   function created")

    # No function URL is created here, on purpose. Public ones are blocked in
    # this account, and an OAC-signed one cannot carry a POST body. The only
    # way in is CloudFront -> HTTP API, which attach-to-cdn.py owns.
    os.remove(zip_path)
    print("\nRun `python attach-to-cdn.py` to wire it up at /api/lead.")


# --------------------------------------------------------------------- test

def test():
    # Through the CDN, which is the only path that carries the origin token.
    url = "https://d288tvmi7qlbjd.cloudfront.net/api/lead"
    payload = {
        "name": "בדיקה אוטומטית", "company": "טאקט בדיקות בע\"מ",
        "phone": "050-0000000", "email": "test-lead@yazam-il.com",
        "projects": "3", "note": "ליד סינתטי מ-deploy.py test",
        "source": "site", "campaign": {"utm_source": "selftest"},
        "startedAt": (time.time() - 60) * 1000,
    }
    import urllib.request
    req = urllib.request.Request(
        url, data=json.dumps(payload, ensure_ascii=False).encode(),
        headers={"Content-Type": "application/json", "origin": "https://yazam-il.com"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            print(r.status, r.read().decode())
    except Exception as e:                       # noqa: BLE001
        body = getattr(e, "read", lambda: b"")().decode("utf-8", "replace")
        print(f"FAILED {type(e).__name__}: {e}\n{body}")
        sys.exit(1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"secrets": put_secrets, "deploy": deploy, "test": test}.get(
        cmd, lambda: sys.exit(__doc__))()
