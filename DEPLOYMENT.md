# 🚀 Literattus AWS ECS Deployment Guide

## Prerequisites

1. **AWS Account** - You need an AWS account with appropriate permissions
2. **AWS Credentials** - Access Key ID and Secret Access Key
3. **RDS Database** - Your MySQL database should already be set up (you mentioned using AWS RDS)

## Step 1: Configure AWS CLI

If you haven't configured AWS CLI yet, run:

```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Your AWS access key
- **AWS Secret Access Key**: Your AWS secret key
- **Default region name**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

**To get AWS credentials:**
1. Log into AWS Console
2. Go to IAM → Users → Your User → Security Credentials
3. Create Access Key
4. Download and save the credentials securely

## Step 2: Run AWS Setup Script

Once AWS CLI is configured, run the setup script:

```bash
cd /home/nelso/Documents/Literattus
./scripts/aws-setup.sh
```

This script will:
- ✅ Create ECR repositories for backend and frontend
- ✅ Create ECS cluster
- ✅ Set up VPC and networking (uses default VPC if available)
- ✅ Create security groups
- ✅ Create Application Load Balancer
- ✅ Create target groups for backend and frontend
- ✅ Configure ALB listeners and routing rules
- ✅ Create CloudWatch log groups

## Step 3: Store Secrets

Store your database credentials and secret key in AWS Secrets Manager:

```bash
./scripts/store-secrets.sh
```

You'll be prompted for:
- RDS Database Host (your RDS endpoint)
- Database User
- Database Password
- Database Name (default: literattus)

The script will also generate a secure SECRET_KEY for you.

## Step 4: Update Task Definitions

After storing secrets, you need to update the task definition files with:
1. Your AWS Account ID
2. The secret ARNs (the script will show these)

**Get your AWS Account ID:**
```bash
aws sts get-caller-identity --query Account --output text
```

**Update the task definition files:**
- Replace `YOUR_ACCOUNT_ID` in both `ecs-task-definition-backend.json` and `ecs-task-definition-frontend.json`
- Update the secret ARNs (the store-secrets.sh script will show you these)

## Step 5: Create ECS Services

After updating task definitions, create the ECS services. The setup script will provide the necessary information (VPC ID, subnets, security group, target group ARNs).

## Step 6: Deploy

Once everything is set up, deploy your application:

```bash
./deploy.sh
```

This will:
- Build Docker images
- Push to ECR
- Register task definitions
- Update ECS services

## Access Your Application

After deployment, access your application via the ALB DNS name (shown in the setup script output):
- Frontend: `http://your-alb-dns-name.us-east-1.elb.amazonaws.com`
- Backend API: `http://your-alb-dns-name.us-east-1.elb.amazonaws.com/api`

## Troubleshooting

### Check ECS Service Status
```bash
aws ecs describe-services --cluster literattus-cluster --services literattus-backend-service literattus-frontend-service --region us-east-1
```

### View Logs
```bash
# Backend logs
aws logs tail /ecs/literattus-backend --follow --region us-east-1

# Frontend logs
aws logs tail /ecs/literattus-frontend --follow --region us-east-1
```

### Check Task Status
```bash
aws ecs list-tasks --cluster literattus-cluster --region us-east-1
```

## Cost Optimization

For a student project (1 month):
- Use Fargate Spot (70% savings) - update services to use Fargate Spot capacity provider
- Use t3.micro RDS instance
- Set up auto-scaling to scale down at night
- Monitor costs in AWS Cost Explorer

## Cleanup (After Project)

To avoid charges after your project:

```bash
# Stop services
aws ecs update-service --cluster literattus-cluster --service literattus-backend-service --desired-count 0 --region us-east-1
aws ecs update-service --cluster literattus-cluster --service literattus-frontend-service --desired-count 0 --region us-east-1

# Delete services
aws ecs delete-service --cluster literattus-cluster --service literattus-backend-service --region us-east-1
aws ecs delete-service --cluster literattus-cluster --service literattus-frontend-service --region us-east-1

# Delete cluster
aws ecs delete-cluster --cluster literattus-cluster --region us-east-1

# Delete ECR repositories
aws ecr delete-repository --repository-name literattus-backend --force --region us-east-1
aws ecr delete-repository --repository-name literattus-frontend --force --region us-east-1

# Delete ALB, target groups, etc. (via AWS Console or CLI)
```



