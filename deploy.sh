#!/bin/bash
set -e

# Configuration - UPDATE THESE VALUES
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_BACKEND="literattus-backend"
ECR_REPO_FRONTEND="literattus-frontend"
CLUSTER_NAME="literattus-cluster"
SERVICE_BACKEND="literattus-backend-service"
SERVICE_FRONTEND="literattus-frontend-service"

echo "🚀 Starting deployment..."
echo "📍 Region: $AWS_REGION"
echo "🆔 Account ID: $AWS_ACCOUNT_ID"

# 1. Login to ECR
echo ""
echo "📦 Logging into ECR..."
aws ecr get-login-REDACTED --region $AWS_REGION | docker login --username AWS --REDACTED-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Build and push backend
echo ""
echo "🔨 Building and pushing backend..."
cd backend
docker build -t $ECR_REPO_BACKEND:latest .
docker tag $ECR_REPO_BACKEND:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_BACKEND:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_BACKEND:latest
cd ..

# 3. Build and push frontend
echo ""
echo "🔨 Building and pushing frontend..."
cd frontend
docker build -t $ECR_REPO_FRONTEND:latest .
docker tag $ECR_REPO_FRONTEND:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_FRONTEND:latest
cd ..

# 4. Update image URLs in task definitions
echo ""
echo "📝 Updating task definitions with image URLs..."
sed -i "s/YOUR_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" ecs-task-definition-backend.json
sed -i "s/YOUR_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" ecs-task-definition-frontend.json

# 5. Register task definitions
echo ""
echo "📋 Registering task definitions..."
aws ecs register-task-definition --cli-input-json file://ecs-task-definition-backend.json --region $AWS_REGION
aws ecs register-task-definition --cli-input-json file://ecs-task-definition-frontend.json --region $AWS_REGION

# 6. Update services (if they exist)
echo ""
echo "🔄 Updating services..."
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_BACKEND --force-new-deployment --region $AWS_REGION 2>/dev/null || echo "⚠️  Backend service not found (will create in Step 4)"
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_FRONTEND --force-new-deployment --region $AWS_REGION 2>/dev/null || echo "⚠️  Frontend service not found (will create in Step 4)"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📌 Next steps:"
echo "   1. Update secret ARNs in task definition files"
echo "   2. Create ECS services (Step 4)"
echo "   3. Configure ALB listeners"

