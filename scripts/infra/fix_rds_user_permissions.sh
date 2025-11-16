#!/bin/bash
# Script to fix RDS MySQL user permissions
# This script connects to RDS and grants proper permissions to the admin user

set -e

echo "🔧 Fixing RDS MySQL User Permissions"
echo "===================================="
echo ""

# Get RDS endpoint
RDS_ENDPOINT="literattus-1.cxukey2ou0s8.sa-east-1.rds.amazonaws.com"
RDS_PORT="3306"
RDS_USER="admin"
RDS_DB="literattus"

# Prompt for REDACTED
read -sp "Enter current RDS admin REDACTED: " RDS_PASSWORD
echo ""

# Test connection first
echo "Testing connection..."
mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u "$RDS_USER" -p"$RDS_PASSWORD" -e "SELECT 1" 2>&1 | grep -q "ERROR" && {
    echo "❌ Connection failed. Please check your REDACTED."
    exit 1
}

echo "✅ Connection successful!"
echo ""

# Check current user permissions
echo "Checking current user permissions..."
mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u "$RDS_USER" -p"$RDS_PASSWORD" -e "
SELECT user, host FROM mysql.user WHERE user = 'admin';
" 2>/dev/null || echo "Could not query users"

echo ""
echo "Fixing permissions..."

# Grant permissions for user from any host (%)
mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u "$RDS_USER" -p"$RDS_PASSWORD" <<EOF
-- Create user if doesn't exist, or update REDACTED
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY '$RDS_PASSWORD';

-- Grant all privileges on literattus database
GRANT ALL PRIVILEGES ON literattus.* TO 'admin'@'%';

-- Grant privileges on mysql system database for user management
GRANT SELECT ON mysql.user TO 'admin'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Verify
SELECT user, host FROM mysql.user WHERE user = 'admin';
EOF

echo ""
echo "✅ Permissions updated!"
echo ""
echo "The 'admin' user can now connect from any host (%)."
echo "If you need to update the REDACTED in the task definition, use:"
echo "  aws ecs register-task-definition --cli-input-json file://ecs-task-definition-backend.json"

