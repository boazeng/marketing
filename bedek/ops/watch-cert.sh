#!/usr/bin/env bash
# Polls ACM and runs `deploy.py create` the moment the certificate is issued.
export AWS_PAGER=""
ARN=arn:aws:acm:us-east-1:824980746386:certificate/00616ad1-8482-40a8-9afd-d7e1e9c43bbb
for i in $(seq 1 90); do
  S=$(aws acm describe-certificate --region us-east-1 --certificate-arn "$ARN" \
        --query 'Certificate.Status' --output text 2>/dev/null)
  if [ "$S" = "ISSUED" ]; then
    echo "certificate ISSUED after ~$((i*40))s"
    python deploy.py create
    exit 0
  fi
  sleep 40
done
echo "still $S after 60 minutes -- check the CNAMEs are DNS-only in Cloudflare"
exit 1
