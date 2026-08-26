# -*- coding: utf-8 -*-
"""
Creates (once) and then updates the AWS delivery for yazam-il.com.

    python deploy.py create     one-time: CloudFront distribution + bucket policy
    python deploy.py publish    build, sync to S3, invalidate the CDN

`create` refuses to run until the ACM certificate is ISSUED, because attaching
an alias to an unissued certificate fails in a way that leaves a half-built
distribution behind.
"""
import io, json, os, shutil, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", "site"))

ACCOUNT = "824980746386"
BUCKET = f"yazam-il-frontend-{ACCOUNT}"
REGION = "us-east-1"
DOMAINS = ["yazam-il.com", "www.yazam-il.com"]
CERT = f"arn:aws:acm:{REGION}:{ACCOUNT}:certificate/00616ad1-8482-40a8-9afd-d7e1e9c43bbb"
OAC = "E1YYX4H177WDDP"
CACHING_OPTIMIZED = "658327ea-f89d-4fab-a63d-7e88639e58f6"  # AWS managed
STATE = os.path.join(HERE, ".distribution-id")


# On Windows the entry point is `aws.cmd`; subprocess without a shell will not
# find a bare "aws" on PATH. Resolving it once here keeps shell=True out of
# every call, which matters because these arguments contain JSON.
AWS = shutil.which("aws") or "aws"
NPX = shutil.which("npx") or "npx"


def aws(*args, parse=True):
    env = dict(os.environ, AWS_PAGER="")
    out = subprocess.run([AWS, *args], capture_output=True, text=True, env=env)
    if out.returncode:
        raise SystemExit(f"aws {' '.join(args[:3])} failed:\n{out.stderr.strip()}")
    return json.loads(out.stdout) if parse and out.stdout.strip() else out.stdout.strip()


def cert_status():
    return aws("acm", "describe-certificate", "--region", REGION,
               "--certificate-arn", CERT, "--query", "Certificate.Status",
               "--output", "text", parse=False)


def distribution_config(ref):
    return {
        "CallerReference": ref,
        "Comment": "yazam-il.com - TACT Bedek marketing site",
        "Enabled": True,
        "Aliases": {"Quantity": len(DOMAINS), "Items": DOMAINS},
        "DefaultRootObject": "index.html",
        "Origins": {"Quantity": 1, "Items": [{
            "Id": "s3-site",
            "DomainName": f"{BUCKET}.s3.{REGION}.amazonaws.com",
            "OriginAccessControlId": OAC,
            "S3OriginConfig": {"OriginAccessIdentity": ""},
        }]},
        "DefaultCacheBehavior": {
            "TargetOriginId": "s3-site",
            "ViewerProtocolPolicy": "redirect-to-https",
            "CachePolicyId": CACHING_OPTIMIZED,
            # The reference distribution has this off. It is a plain miss on a
            # text-heavy site: the CSS goes 13.6kB -> 3.7kB and the JS
            # 159kB -> 52kB over the wire.
            "Compress": True,
            "AllowedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"],
                               "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}},
        },
        # S3 behind OAC answers a missing key with 403 AccessDenied in XML, not
        # 404 -- ListBucket is deliberately not granted. Both are mapped to a
        # real 404 page that still returns 404, so a typo does not silently
        # serve the homepage and get it indexed twice.
        "CustomErrorResponses": {"Quantity": 2, "Items": [
            {"ErrorCode": c, "ResponseCode": "404",
             "ResponsePagePath": "/404.html", "ErrorCachingMinTTL": 60}
            for c in (403, 404)
        ]},
        "ViewerCertificate": {
            "ACMCertificateArn": CERT,
            "SSLSupportMethod": "sni-only",
            "MinimumProtocolVersion": "TLSv1.2_2021",
        },
        "HttpVersion": "http2and3",
        "IsIPV6Enabled": True,
        "PriceClass": "PriceClass_All",
    }


def create():
    status = cert_status()
    if status != "ISSUED":
        raise SystemExit(
            f"certificate is {status}, not ISSUED -- nothing created.\n"
            "ACM rechecks DNS every few minutes; run this again once it flips.")

    if os.path.exists(STATE):
        raise SystemExit(f"distribution {io.open(STATE).read().strip()} already exists; "
                         "use `publish`.")

    dist = aws("cloudfront", "create-distribution",
               "--distribution-config", json.dumps(distribution_config(f"yazam-il-{int(time.time())}")))
    did = dist["Distribution"]["Id"]
    domain = dist["Distribution"]["DomainName"]
    io.open(STATE, "w").write(did)

    # The bucket stays private. Only this one distribution may read it.
    aws("s3api", "put-bucket-policy", "--bucket", BUCKET, "--policy", json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "AllowCloudFrontServicePrincipalReadOnly",
            "Effect": "Allow",
            "Principal": {"Service": "cloudfront.amazonaws.com"},
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{BUCKET}/*",
            "Condition": {"StringEquals": {
                "AWS:SourceArn": f"arn:aws:cloudfront::{ACCOUNT}:distribution/{did}"}},
        }],
    }), parse=False)

    print(f"distribution {did}\ncloudfront domain {domain}\n")
    print("Add these two records in Cloudflare, both Proxy status = DNS only:\n")
    for name in ("yazam-il.com", "www"):
        print(f"  CNAME   {name:14} -> {domain}")
    print("\nCloudFront takes ~5-15 minutes to deploy before it serves.")


def publish():
    if not os.path.exists(STATE):
        raise SystemExit("no distribution yet -- run `create` first.")
    did = io.open(STATE).read().strip()

    subprocess.run([sys.executable, "sync-brand.py"], cwd=SITE, check=True)
    subprocess.run([NPX, "vite", "build"], cwd=SITE, check=True)

    # Hashed assets are immutable and cached hard; the HTML must never be, or a
    # deploy takes an hour to become visible.
    aws("s3", "sync", os.path.join(SITE, "dist"), f"s3://{BUCKET}/", "--delete",
        "--exclude", "*.html", "--cache-control", "public,max-age=31536000,immutable",
        parse=False)
    aws("s3", "sync", os.path.join(SITE, "dist"), f"s3://{BUCKET}/", "--delete",
        "--exclude", "*", "--include", "*.html",
        "--cache-control", "public,max-age=0,must-revalidate", parse=False)

    inv = aws("cloudfront", "create-invalidation", "--distribution-id", did,
              "--paths", "/*")
    print(f"published. invalidation {inv['Invalidation']['Id']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "create":
        create()
    elif cmd == "publish":
        publish()
    else:
        raise SystemExit(__doc__)
