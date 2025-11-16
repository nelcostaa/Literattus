#!/bin/bash
# Script to store secrets in AWS Secrets Manager
# Usage: ./scripts/store-secrets.sh

set -e

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🔐 Storing Secrets in AWS Secrets Manager"
echo "📍 Region: $AWS_REGION"
echo "🆔 Account ID: $AWS_ACCOUNT_ID"
echo ""

# Prompt for database credentials
read -p "Enter RDS Database Host (e.g., your-db.xxxxx.rds.amazonaws.com): " DB_HOST
read -p "Enter Database User: " DB_USER
read -sp "Enter Database Password: " DB_PASSWORD
echo ""
read -p "Enter Database Name [literattus]: " DB_NAME
DB_NAME=${DB_NAME:-literattus}

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)

echo ""
echo "📝 Storing secrets..."

# Store DB Host
aws secretsmanager create-secret \
    --name literattus/db-host \
    --secret-string "$DB_HOST" \
    --region $AWS_REGION \
    --description "Literattus database host" \
    2>/dev/null || \
aws secretsmanager update-secret \
    --secret-id literattus/db-host \
    --secret-string "$DB_HOST" \
    --region $AWS_REGION > /dev/null
echo "  ✅ Stored DB_HOST"

# Store DB User
aws secretsmanager create-secret \
    --name literattus/db-user \
    --secret-string "$DB_USER" \
    --region $AWS_REGION \
    --description "Literattus database user" \
    2>/dev/null || \
aws secretsmanager update-secret \
    --secret-id literattus/db-user \
    --secret-string "$DB_USER" \
    --region $AWS_REGION > /dev/null
echo "  ✅ Stored DB_USER"

# Store DB Password
aws secretsmanager create-secret \
    --name literattus/db-REDACTED \
    --secret-string "$DB_PASSWORD" \
    --region $AWS_REGION \
    --description "Literattus database REDACTED" \
    2>/dev/null || \
aws secretsmanager update-secret \
    --secret-id literattus/db-REDACTED \
    --secret-string "$DB_PASSWORD" \
    --region $AWS_REGION > /dev/null
echo "  ✅ Stored DB_PASSWORD"

# Store Secret Key
aws secretsmanager create-secret \
    --name literattus/secret-key \
    --secret-string "$SECRET_KEY" \
    --region $AWS_REGION \
    --description "Literattus application secret key" \
    2>/dev/null || \
aws secretsmanager update-secret \
    --secret-id literattus/secret-key \
    --secret-string "$SECRET_KEY" \
    --region $AWS_REGION > /dev/null
echo "  ✅ Stored SECRET_KEY"

echo ""
echo "✅ All secrets stored successfully!"
echo ""
echo "📋 Secret ARNs (update these in task definition files):"
echo "  DB_HOST: arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:literattus/db-host"
echo "  DB_USER: arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:literattus/db-user"
echo "  DB_PASSWORD: arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:literattus/db-REDACTED"
echo "  SECRET_KEY: arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:literattus/secret-key"
echo ""



