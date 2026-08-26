# -*- coding: utf-8 -*-
"""
Puts the lead proxy behind the site's CloudFront distribution at /api/lead,
through an HTTP API.

    python attach-to-cdn.py

Why an API Gateway HTTP API and not the Lambda's own function URL -- both were
tried, in this order:

  1. A PUBLIC function URL returns 403 in this account regardless of the
     resource policy. Public Lambda URLs are blocked at the account level.

  2. Fronting the function URL with a CloudFront OAC fails too. CloudFront's
     sigv4 signature for a lambda-type OAC does NOT cover the request body, so
     every POST that carries one comes back InvalidSignatureException. No
     setting changes that.

     It is a nasty one to diagnose, because our own 403 -> /404.html error
     mapping swallows it: the symptom is a plain 404 with `Server: AmazonS3`
     and NOTHING in the Lambda's logs. Turning CustomErrorResponses off is
     what makes the real status visible.

  3. CloudFront -> HTTP API -> Lambda is the shape tact-crm already runs, so
     the account keeps one pattern instead of three.

The HTTP API endpoint is reachable directly as well as through the CDN, so
CloudFront attaches a shared secret header and the function refuses anything
without it. Public surface stays at exactly one URL.
"""
import io, json, os, secrets, shutil, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNT = "824980746386"
REGION = "us-east-1"
FN = "yazam-il-lead-proxy"
API_NAME = "yazam-il-lead-api"
DIST = io.open(os.path.join(HERE, "..", ".distribution-id")).read().strip()
PATTERN = "api/lead"          # CloudFront path patterns are RELATIVE
P_EDGE = "yazam-il-edge-secret"

CACHING_DISABLED = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
# Custom: forwards only the two headers the handler reads. Every managed policy
# that forwards enough also forwards Authorization.
LEAN_ORIGIN_REQUEST = "ef052be4-aa5a-4725-9188-57d33750e8dc"

AWS = shutil.which("aws") or "aws"


def aws(*args, parse=True, check=True):
    out = subprocess.run([AWS, *args], capture_output=True, text=True,
                         env=dict(os.environ, AWS_PAGER=""))
    if check and out.returncode:
        raise SystemExit(f"aws {' '.join(args[:3])} failed:\n{out.stderr.strip()}")
    if out.returncode:
        return None
    return json.loads(out.stdout) if parse and out.stdout.strip() else out.stdout.strip()


def ensure_edge_secret():
    existing = aws("ssm", "get-parameter", "--region", REGION, "--name", P_EDGE,
                   "--with-decryption", "--query", "Parameter.Value", "--output", "text",
                   parse=False, check=False)
    if existing:
        return existing
    value = secrets.token_urlsafe(32)
    aws("ssm", "put-parameter", "--region", REGION, "--name", P_EDGE,
        "--type", "SecureString", "--overwrite", "--value", value, parse=False)
    return value


def ensure_api():
    apis = aws("apigatewayv2", "get-apis", "--region", REGION,
               "--query", f"Items[?Name=='{API_NAME}'].ApiId", "--output", "text",
               parse=False)
    api_id = apis.split()[0] if apis and apis != "None" else None
    if api_id:
        return api_id

    fn_arn = aws("lambda", "get-function", "--region", REGION, "--function-name", FN,
                 "--query", "Configuration.FunctionArn", "--output", "text", parse=False)
    # --target builds the $default route, the proxy integration and an
    # auto-deployed $default stage in one call.
    api_id = aws("apigatewayv2", "create-api", "--region", REGION, "--name", API_NAME,
                 "--protocol-type", "HTTP", "--target", fn_arn,
                 "--query", "ApiId", "--output", "text", parse=False)
    aws("lambda", "add-permission", "--region", REGION, "--function-name", FN,
        "--statement-id", "AllowApiGateway", "--action", "lambda:InvokeFunction",
        "--principal", "apigateway.amazonaws.com",
        "--source-arn", f"arn:aws:execute-api:{REGION}:{ACCOUNT}:{api_id}/*/*",
        parse=False, check=False)
    return api_id


def main():
    edge_secret = ensure_edge_secret()
    api_id = ensure_api()
    host = f"{api_id}.execute-api.{REGION}.amazonaws.com"
    print(f"   http api {api_id}")

    # Nothing uses the function URL now; remove it rather than leave a second,
    # unreachable way in.
    aws("lambda", "delete-function-url-config", "--region", REGION,
        "--function-name", FN, parse=False, check=False)
    aws("lambda", "remove-permission", "--region", REGION, "--function-name", FN,
        "--statement-id", "AllowCloudFront", parse=False, check=False)

    aws("lambda", "update-function-configuration", "--region", REGION,
        "--function-name", FN, "--environment", json.dumps({"Variables": {
            "CRM_URL": "https://crm-db.newavera.co.il/api/v1/customers",
            "CRM_KEY_PARAM": "yazam-il-crm-api-key",
            "TG_TOKEN_PARAM": "yazam-il-telegram-token",
            "TG_CHAT_PARAM": "yazam-il-telegram-chat",
            "EDGE_SECRET_PARAM": P_EDGE,
        }}), parse=False)
    aws("lambda", "wait", "function-updated", "--region", REGION,
        "--function-name", FN, parse=False)

    cur = aws("cloudfront", "get-distribution-config", "--id", DIST)
    etag, cfg = cur["ETag"], cur["DistributionConfig"]

    cfg["Origins"]["Items"] = [o for o in cfg["Origins"]["Items"] if o["Id"] != "lead-proxy"]
    cfg["Origins"]["Items"].append({
        "Id": "lead-proxy",
        "DomainName": host,
        "OriginPath": "",
        "CustomHeaders": {"Quantity": 1, "Items": [
            {"HeaderName": "x-origin-token", "HeaderValue": edge_secret}]},
        "OriginShield": {"Enabled": False},
        "ConnectionAttempts": 3,
        "ConnectionTimeout": 10,
        "CustomOriginConfig": {
            "HTTPPort": 80, "HTTPSPort": 443,
            "OriginProtocolPolicy": "https-only",
            "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]},
            "OriginReadTimeout": 30,
            # Optional on create, MANDATORY on update.
            "OriginKeepaliveTimeout": 5,
        },
    })
    cfg["Origins"]["Quantity"] = len(cfg["Origins"]["Items"])

    behaviours = [b for b in (cfg.get("CacheBehaviors", {}).get("Items") or [])
                  if b["PathPattern"].lstrip("/") != PATTERN]
    behaviours.append({
        "PathPattern": PATTERN,
        "TargetOriginId": "lead-proxy",
        "ViewerProtocolPolicy": "https-only",
        "CachePolicyId": CACHING_DISABLED,
        "OriginRequestPolicyId": LEAN_ORIGIN_REQUEST,
        "AllowedMethods": {
            "Quantity": 7,
            "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
            "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
        },
        "Compress": True,
        # UpdateDistribution validates the full legacy shape and reports one
        # missing field per round trip, so all of them are stated up front.
        "SmoothStreaming": False,
        "FieldLevelEncryptionId": "",
        "TrustedSigners": {"Enabled": False, "Quantity": 0},
        "TrustedKeyGroups": {"Enabled": False, "Quantity": 0},
        "LambdaFunctionAssociations": {"Quantity": 0, "Items": []},
        "FunctionAssociations": {"Quantity": 0, "Items": []},
    })
    cfg["CacheBehaviors"] = {"Quantity": len(behaviours), "Items": behaviours}

    # Restore the error pages -- debugging turns them off to see real statuses.
    cfg["CustomErrorResponses"] = {"Quantity": 2, "Items": [
        {"ErrorCode": c, "ResponseCode": "404", "ResponsePagePath": "/404.html",
         "ErrorCachingMinTTL": 60} for c in (403, 404)]}

    aws("cloudfront", "update-distribution", "--id", DIST, "--if-match", etag,
        "--distribution-config", json.dumps(cfg), parse=False)
    print(f"   distribution {DIST}: /{PATTERN} -> {host}")
    print(f"\nVITE_LEAD_ENDPOINT=/{PATTERN}   (same-origin, no CORS)")


if __name__ == "__main__":
    main()
