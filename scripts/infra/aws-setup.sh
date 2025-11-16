#!/usr/bin/env bash
set -euo pipefail

# Simple AWS setup for Literattus (idempotent-ish)
AWS_REGION="${AWS_REGION:-sa-east-1}"
CLUSTER_NAME="${CLUSTER_NAME:-literattus-cluster}"
ECR_REPO_BACKEND="${ECR_REPO_BACKEND:-literattus-backend}"
ECR_REPO_FRONTEND="${ECR_REPO_FRONTEND:-literattus-frontend}"

echo "Starting AWS setup in region: $AWS_REGION"

# Get AWS account id
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --region "$AWS_REGION")
echo "AWS account: $AWS_ACCOUNT_ID"

echo "Creating ECR repositories..."
aws ecr create-repository --repository-name "$ECR_REPO_BACKEND" --region "$AWS_REGION" >/dev/null 2>&1 || echo "ECR repo $ECR_REPO_BACKEND exists"
aws ecr create-repository --repository-name "$ECR_REPO_FRONTEND" --region "$AWS_REGION" >/dev/null 2>&1 || echo "ECR repo $ECR_REPO_FRONTEND exists"

echo "Creating ECS cluster..."
aws ecs create-cluster --cluster-name "$CLUSTER_NAME" --region "$AWS_REGION" >/dev/null 2>&1 || echo "ECS cluster $CLUSTER_NAME exists"

echo "Ensuring CloudWatch log groups..."
aws logs create-log-group --log-group-name /ecs/literattus-backend --region "$AWS_REGION" >/dev/null 2>&1 || true
aws logs create-log-group --log-group-name /ecs/literattus-frontend --region "$AWS_REGION" >/dev/null 2>&1 || true

# Use default VPC and subnets
VPC_ID=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query "Vpcs[0].VpcId" --output text --region "$AWS_REGION")
if [ -z "$VPC_ID" ] || [ "$VPC_ID" == "None" ]; then
  echo "No default VPC found; creating one..."
  VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text --region "$AWS_REGION")
  aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames --region "$AWS_REGION"
fi
echo "Using VPC: $VPC_ID"

SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[?MapPublicIpOnLaunch==\`true\`].SubnetId" --output text --region "$AWS_REGION")
if [ -z "$SUBNETS" ]; then
  echo "Creating two public subnets..."
  SUBNET1=$(aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block 10.0.1.0/24 --availability-zone "${AWS_REGION}a" --query "Subnet.SubnetId" --output text --region "$AWS_REGION")
  SUBNET2=$(aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block 10.0.2.0/24 --availability-zone "${AWS_REGION}b" --query "Subnet.SubnetId" --output text --region "$AWS_REGION")
  SUBNETS="$SUBNET1 $SUBNET2"
fi
# Build an array of subnet ids and pick first two
read -r -a SUBNET_IDS <<< "$SUBNETS"
SUBNET_1=${SUBNET_IDS[0]}
SUBNET_2=${SUBNET_IDS[1]:-$SUBNET_1}
echo "Using subnets: ${SUBNET_IDS[@]}"

echo "Creating security group..."
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=literattus-sg" "Name=vpc-id,Values=$VPC_ID" --query "SecurityGroups[0].GroupId" --output text --region "$AWS_REGION" 2>/dev/null || echo "")
if [ -z "$SG_ID" ] || [ "$SG_ID" == "None" ]; then
  SG_ID=$(aws ec2 create-security-group --group-name literattus-sg --description "Literattus security group" --vpc-id "$VPC_ID" --query "GroupId" --output text --region "$AWS_REGION")
  aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0 --region "$AWS_REGION" || true
  aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 443 --cidr 0.0.0.0/0 --region "$AWS_REGION" || true
fi
echo "Using security group: $SG_ID"

echo "Creating ALB..."
ALB_ARN=$(aws elbv2 describe-load-balancers --names literattus-alb --region "$AWS_REGION" --query "LoadBalancers[0].LoadBalancerArn" --output text 2>/dev/null || echo "")
if [ -z "$ALB_ARN" ] || [ "$ALB_ARN" == "None" ]; then
  ALB_ARN=$(aws elbv2 create-load-balancer --name literattus-alb --subnets "$SUBNET_1" "$SUBNET_2" --security-groups "$SG_ID" --region "$AWS_REGION" --query "LoadBalancers[0].LoadBalancerArn" --output text)
fi
ALB_DNS=$(aws elbv2 describe-load-balancers --load-balancer-arns "$ALB_ARN" --region "$AWS_REGION" --query "LoadBalancers[0].DNSName" --output text)
echo "ALB DNS: $ALB_DNS"

echo "Creating target groups..."
BACKEND_TG_ARN=$(aws elbv2 describe-target-groups --names literattus-backend-tg --region "$AWS_REGION" --query "TargetGroups[0].TargetGroupArn" --output text 2>/dev/null || echo "")
if [ -z "$BACKEND_TG_ARN" ] || [ "$BACKEND_TG_ARN" == "None" ]; then
  BACKEND_TG_ARN=$(aws elbv2 create-target-group --name literattus-backend-tg --protocol HTTP --port 8000 --vpc-id "$VPC_ID" --target-type ip --health-check-path /health --region "$AWS_REGION" --query "TargetGroups[0].TargetGroupArn" --output text)
fi
FRONTEND_TG_ARN=$(aws elbv2 describe-target-groups --names literattus-frontend-tg --region "$AWS_REGION" --query "TargetGroups[0].TargetGroupArn" --output text 2>/dev/null || echo "")
if [ -z "$FRONTEND_TG_ARN" ] || [ "$FRONTEND_TG_ARN" == "None" ]; then
  FRONTEND_TG_ARN=$(aws elbv2 create-target-group --name literattus-frontend-tg --protocol HTTP --port 8080 --vpc-id "$VPC_ID" --target-type ip --health-check-path / --region "$AWS_REGION" --query "TargetGroups[0].TargetGroupArn" --output text)
fi
echo "Backend TG: $BACKEND_TG_ARN"
echo "Frontend TG: $FRONTEND_TG_ARN"

echo "Creating listener and rules..."
LISTENER_ARN=$(aws elbv2 describe-listeners --load-balancer-arn "$ALB_ARN" --region "$AWS_REGION" --query "Listeners[0].ListenerArn" --output text 2>/dev/null || echo "")
if [ -z "$LISTENER_ARN" ] || [ "$LISTENER_ARN" == "None" ]; then
  LISTENER_ARN=$(aws elbv2 create-listener --load-balancer-arn "$ALB_ARN" --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn="$FRONTEND_TG_ARN" --region "$AWS_REGION" --query "Listeners[0].ListenerArn" --output text)
fi
# create rule for /api/* if not present
RULES=$(aws elbv2 describe-rules --listener-arn "$LISTENER_ARN" --region "$AWS_REGION" --query "Rules[].Conditions[].Values[]" --output text || echo "")
if ! echo "$RULES" | grep -q "/api/*" 2>/dev/null; then
  aws elbv2 create-rule --listener-arn "$LISTENER_ARN" --priority 10 --conditions Field=path-pattern,Values='/api/*' --actions Type=forward,TargetGroupArn="$BACKEND_TG_ARN" --region "$AWS_REGION" >/dev/null
fi

echo "Setup complete."
echo "ALB DNS: $ALB_DNS"
echo "Target Groups: backend=$BACKEND_TG_ARN frontend=$FRONTEND_TG_ARN"
echo "Cluster: $CLUSTER_NAME"
echo "ECR repos: $ECR_REPO_BACKEND, $ECR_REPO_FRONTEND"
