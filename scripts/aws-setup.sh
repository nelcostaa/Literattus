#!/bin/bash
# AWS Setup Script for Literattus ECS Deployment
# This script sets up all necessary AWS resources for ECS deployment

set -e

AWS_REGION="us-east-1"
CLUSTER_NAME="literattus-cluster"
ECR_REPO_BACKEND="literattus-backend"
ECR_REPO_FRONTEND="literattus-frontend"

echo "🚀 Starting AWS Setup for Literattus..."
echo "📍 Region: $AWS_REGION"
echo ""

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "❌ Error: AWS CLI not configured or credentials invalid"
    echo "Please run: aws configure"
    echo "You'll need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region: us-east-1"
    echo "  - Default output format: json"
    exit 1
fi

echo "✅ AWS Account ID: $AWS_ACCOUNT_ID"
echo ""

# Step 1: Create ECR Repositories
echo "📦 Step 1: Creating ECR repositories..."
aws ecr create-repository --repository-name $ECR_REPO_BACKEND --region $AWS_REGION 2>/dev/null || echo "  ⚠️  Backend repository already exists"
aws ecr create-repository --repository-name $ECR_REPO_FRONTEND --region $AWS_REGION 2>/dev/null || echo "  ⚠️  Frontend repository already exists"
echo "✅ ECR repositories ready"
echo ""

# Step 2: Create ECS Cluster
echo "🏗️  Step 2: Creating ECS cluster..."
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION 2>/dev/null || echo "  ⚠️  Cluster already exists"
echo "✅ ECS cluster ready"
echo ""

# Step 3: Get or create default VPC
echo "🌐 Step 3: Setting up networking..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $AWS_REGION 2>/dev/null || echo "")

if [ -z "$VPC_ID" ] || [ "$VPC_ID" == "None" ]; then
    echo "  ⚠️  No default VPC found. Creating VPC..."
    VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region $AWS_REGION --query "Vpc.VpcId" --output text)
    aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames --region $AWS_REGION
    aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support --region $AWS_REGION
    echo "  ✅ Created VPC: $VPC_ID"
else
    echo "  ✅ Using default VPC: $VPC_ID"
fi

# Get subnets
SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text --region $AWS_REGION)
SUBNET_IDS=($SUBNETS)
SUBNET_1=${SUBNET_IDS[0]}
SUBNET_2=${SUBNET_IDS[1]}

if [ -z "$SUBNET_1" ]; then
    echo "  ⚠️  No subnets found. Creating subnets..."
    SUBNET_1=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ${AWS_REGION}a --region $AWS_REGION --query "Subnet.SubnetId" --output text)
    SUBNET_2=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ${AWS_REGION}b --region $AWS_REGION --query "Subnet.SubnetId" --output text)
    echo "  ✅ Created subnets: $SUBNET_1, $SUBNET_2"
else
    echo "  ✅ Using subnets: $SUBNET_1, $SUBNET_2"
fi

# Get or create security group
SG_ID=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID" "Name=group-name,Values=literattus-sg" --query "SecurityGroups[0].GroupId" --output text --region $AWS_REGION 2>/dev/null || echo "")

if [ -z "$SG_ID" ] || [ "$SG_ID" == "None" ]; then
    echo "  Creating security group..."
    SG_ID=$(aws ec2 create-security-group --group-name literattus-sg --description "Literattus security group" --vpc-id $VPC_ID --region $AWS_REGION --query "GroupId" --output text)
    
    # Allow HTTP and HTTPS
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $AWS_REGION 2>/dev/null || true
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $AWS_REGION 2>/dev/null || true
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $AWS_REGION 2>/dev/null || true
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8080 --cidr 0.0.0.0.0/0 --region $AWS_REGION 2>/dev/null || true
    
    echo "  ✅ Created security group: $SG_ID"
else
    echo "  ✅ Using security group: $SG_ID"
fi

echo "✅ Networking ready"
echo ""

# Step 4: Create CloudWatch Log Groups
echo "📊 Step 4: Creating CloudWatch log groups..."
aws logs create-log-group --log-group-name /ecs/literattus-backend --region $AWS_REGION 2>/dev/null || echo "  ⚠️  Backend log group already exists"
aws logs create-log-group --log-group-name /ecs/literattus-frontend --region $AWS_REGION 2>/dev/null || echo "  ⚠️  Frontend log group already exists"
echo "✅ CloudWatch log groups ready"
echo ""

# Step 5: Create Application Load Balancer
echo "⚖️  Step 5: Creating Application Load Balancer..."
ALB_ARN=$(aws elbv2 describe-load-balancers --names literattus-alb --region $AWS_REGION --query "LoadBalancers[0].LoadBalancerArn" --output text 2>/dev/null || echo "")

if [ -z "$ALB_ARN" ] || [ "$ALB_ARN" == "None" ]; then
    ALB_ARN=$(aws elbv2 create-load-balancer \
        --name literattus-alb \
        --subnets $SUBNET_1 $SUBNET_2 \
        --security-groups $SG_ID \
        --region $AWS_REGION \
        --query "LoadBalancers[0].LoadBalancerArn" \
        --output text)
    echo "  ✅ Created ALB: $ALB_ARN"
else
    echo "  ✅ ALB already exists: $ALB_ARN"
fi

ALB_DNS=$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --region $AWS_REGION --query "LoadBalancers[0].DNSName" --output text)
echo "  📍 ALB DNS: $ALB_DNS"
echo ""

# Step 6: Create Target Groups
echo "🎯 Step 6: Creating target groups..."

# Backend target group
BACKEND_TG_ARN=$(aws elbv2 describe-target-groups --names literattus-backend-tg --region $AWS_REGION --query "TargetGroups[0].TargetGroupArn" --output text 2>/dev/null || echo "")

if [ -z "$BACKEND_TG_ARN" ] || [ "$BACKEND_TG_ARN" == "None" ]; then
    BACKEND_TG_ARN=$(aws elbv2 create-target-group \
        --name literattus-backend-tg \
        --protocol HTTP \
        --port 8000 \
        --vpc-id $VPC_ID \
        --target-type ip \
        --health-check-path /health \
        --health-check-interval-seconds 30 \
        --health-check-timeout-seconds 5 \
        --healthy-threshold-count 2 \
        --unhealthy-threshold-count 3 \
        --region $AWS_REGION \
        --query "TargetGroups[0].TargetGroupArn" \
        --output text)
    echo "  ✅ Created backend target group: $BACKEND_TG_ARN"
else
    echo "  ✅ Backend target group already exists: $BACKEND_TG_ARN"
fi

# Frontend target group
FRONTEND_TG_ARN=$(aws elbv2 describe-target-groups --names literattus-frontend-tg --region $AWS_REGION --query "TargetGroups[0].TargetGroupArn" --output text 2>/dev/null || echo "")

if [ -z "$FRONTEND_TG_ARN" ] || [ "$FRONTEND_TG_ARN" == "None" ]; then
    FRONTEND_TG_ARN=$(aws elbv2 create-target-group \
        --name literattus-frontend-tg \
        --protocol HTTP \
        --port 8080 \
        --vpc-id $VPC_ID \
        --target-type ip \
        --health-check-path / \
        --health-check-interval-seconds 30 \
        --health-check-timeout-seconds 5 \
        --healthy-threshold-count 2 \
        --unhealthy-threshold-count 3 \
        --region $AWS_REGION \
        --query "TargetGroups[0].TargetGroupArn" \
        --output text)
    echo "  ✅ Created frontend target group: $FRONTEND_TG_ARN"
else
    echo "  ✅ Frontend target group already exists: $FRONTEND_TG_ARN"
fi

echo "✅ Target groups ready"
echo ""

# Step 7: Create ALB Listeners
echo "🔊 Step 7: Creating ALB listeners..."

# Get default listener
LISTENER_ARN=$(aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --region $AWS_REGION --query "Listeners[0].ListenerArn" --output text 2>/dev/null || echo "")

if [ -z "$LISTENER_ARN" ] || [ "$LISTENER_ARN" == "None" ]; then
    # Create default listener (port 80) routing to frontend
    LISTENER_ARN=$(aws elbv2 create-listener \
        --load-balancer-arn $ALB_ARN \
        --protocol HTTP \
        --port 80 \
        --default-actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN \
        --region $AWS_REGION \
        --query "Listeners[0].ListenerArn" \
        --output text)
    echo "  ✅ Created default listener (port 80 -> frontend)"
fi

# Add rule for /api/* to backend
RULE_EXISTS=$(aws elbv2 describe-rules --listener-arn $LISTENER_ARN --region $AWS_REGION --query "Rules[?Priority=='1']" --output text 2>/dev/null || echo "")

if [ -z "$RULE_EXISTS" ]; then
    aws elbv2 create-rule \
        --listener-arn $LISTENER_ARN \
        --priority 1 \
        --conditions Field=path-pattern,Values='/api/*' \
        --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
        --region $AWS_REGION > /dev/null
    echo "  ✅ Created rule: /api/* -> backend"
else
    echo "  ✅ Rule already exists: /api/* -> backend"
fi

echo "✅ ALB listeners configured"
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════"
echo "✅ AWS Setup Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📋 Summary:"
echo "  AWS Account ID: $AWS_ACCOUNT_ID"
echo "  Region: $AWS_REGION"
echo "  Cluster: $CLUSTER_NAME"
echo "  VPC ID: $VPC_ID"
echo "  Security Group: $SG_ID"
echo "  Subnets: $SUBNET_1, $SUBNET_2"
echo "  ALB DNS: $ALB_DNS"
echo "  Backend Target Group: $BACKEND_TG_ARN"
echo "  Frontend Target Group: $FRONTEND_TG_ARN"
echo ""
echo "📌 Next Steps:"
echo "  1. Store secrets in AWS Secrets Manager (see below)"
echo "  2. Update task definitions with your Account ID and secret ARNs"
echo "  3. Create ECS services"
echo "  4. Deploy using ./deploy.sh"
echo ""
echo "🔐 To store secrets, run:"
echo "  ./scripts/store-secrets.sh"
echo ""

