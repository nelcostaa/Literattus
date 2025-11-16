#!/usr/bin/env bash
set -euo pipefail
# Minimal reproducible check: fail if any target in backend/frontend TG is not healthy
REGION="sa-east-1"
TG_BACK="arn:aws:elasticloadbalancing:sa-east-1:147054060547:targetgroup/literattus-backend-tg/f54b6864f9958379"
TG_FRONT="arn:aws:elasticloadbalancing:sa-east-1:147054060547:targetgroup/literattus-frontend-tg/3b8f78db66ec5951"

check_tg() {
  local tg=$1
  local name=$2
  states=$(/usr/local/bin/aws elbv2 describe-target-health --target-group-arn "$tg" --region "$REGION" --query 'TargetHealthDescriptions[*].TargetHealth.State' --output text)
  echo "$name target states: $states"
  for s in $states; do
    if [ "$s" != "healthy" ]; then
      echo "FAIL: $name has non-healthy target state: $s"
      return 1
    fi
  done
  echo "OK: $name all healthy"
  return 0
}

echo "Checking ALB target groups in $REGION..."
err=0
check_tg "$TG_BACK" "backend" || err=1
check_tg "$TG_FRONT" "frontend" || err=1
if [ $err -ne 0 ]; then
  echo "ALB target health check FAILED"
  exit 2
fi
echo "ALB target health check PASSED"
exit 0

