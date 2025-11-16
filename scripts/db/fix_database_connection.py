#!/usr/bin/env python3
"""
Fix database connection issues by:
1. Testing connection with credentials from backend/.env
2. Fixing MySQL user permissions to allow connections from any host
3. Updating ECS task definition with correct REDACTED
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import pymysql
import subprocess

# Load backend .env
project_root = Path(__file__).parent.parent
backend_env = project_root / "backend" / ".env"

if not backend_env.exists():
    print(f"❌ Error: {backend_env} not found")
    print("Please ensure backend/.env exists with DB credentials")
    sys.exit(1)

load_dotenv(backend_env)

# Get credentials from .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "literattus")

if not all([DB_HOST, DB_USER, DB_PASSWORD]):
    print("❌ Error: Missing DB credentials in backend/.env")
    print("Required: DB_HOST, DB_USER, DB_PASSWORD")
    sys.exit(1)

print("=" * 70)
print("Database Connection Fix Script")
print("=" * 70)
print(f"Host: {DB_HOST}")
print(f"User: {DB_USER}")
print(f"Database: {DB_NAME}")
print()

# Step 1: Test connection with .env credentials
print("Step 1: Testing connection with .env credentials...")
try:
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        REDACTED=DB_PASSWORD,
        database=DB_NAME,
        connect_timeout=10
    )
    print("✅ Connection successful with .env credentials!")
    conn.close()
except pymysql.Error as e:
    print(f"❌ Connection failed: {e}")
    print("\nPossible issues:")
    print("1. Password in .env is incorrect")
    print("2. User doesn't have permission to connect from this IP")
    print("3. RDS security group doesn't allow connections")
    sys.exit(1)

# Step 2: Fix MySQL user permissions
print("\nStep 2: Fixing MySQL user permissions...")
try:
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        REDACTED=DB_PASSWORD,
        database=DB_NAME,
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    # Check current user hosts
    cursor.execute("SELECT user, host FROM mysql.user WHERE user = %s", (DB_USER,))
    users = cursor.fetchall()
    print(f"Current user entries: {users}")
    
    # Create/update user for any host (%)
    cursor.execute(f"""
        CREATE USER IF NOT EXISTS '{DB_USER}'@'%' IDENTIFIED BY '{DB_PASSWORD}'
    """)
    
    # Grant privileges
    cursor.execute(f"""
        GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'%'
    """)
    
    cursor.execute("FLUSH PRIVILEGES")
    
    # Verify
    cursor.execute("SELECT user, host FROM mysql.user WHERE user = %s", (DB_USER,))
    users_after = cursor.fetchall()
    print(f"User entries after fix: {users_after}")
    
    cursor.close()
    conn.close()
    print("✅ User permissions fixed!")
    
except Exception as e:
    print(f"⚠️  Warning: Could not fix permissions: {e}")
    print("You may need to run this manually:")
    print(f"  CREATE USER IF NOT EXISTS '{DB_USER}'@'%' IDENTIFIED BY 'YOUR_PASSWORD';")
    print(f"  GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'%';")
    print("  FLUSH PRIVILEGES;")

# Step 3: Update ECS task definition
print("\nStep 3: Updating ECS task definition...")
task_def_path = project_root / "ecs-task-definition-backend.json"

if not task_def_path.exists():
    print(f"⚠️  Task definition not found: {task_def_path}")
    print("Skipping task definition update")
else:
    try:
        with open(task_def_path, 'r') as f:
            task_def = json.load(f)
        
        # Update DB_PASSWORD in environment variables
        updated = False
        for env_var in task_def['containerDefinitions'][0].get('environment', []):
            if env_var['name'] == 'DB_PASSWORD':
                if env_var['value'] != DB_PASSWORD:
                    print(f"Updating DB_PASSWORD in task definition...")
                    env_var['value'] = DB_PASSWORD
                    updated = True
                else:
                    print("DB_PASSWORD already correct in task definition")
                break
        
        if updated:
            with open(task_def_path, 'w') as f:
                json.dump(task_def, f, indent=2)
            print("✅ Task definition updated!")
            print("\nNext steps:")
            print("1. Review the updated task definition")
            print("2. Register new task definition: aws ecs register-task-definition --cli-input-json file://ecs-task-definition-backend.json")
            print("3. Update service: aws ecs update-service --cluster literattus-cluster --service literattus-backend-service --force-new-deployment")
        else:
            print("✅ Task definition already has correct REDACTED")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not update task definition: {e}")

print("\n" + "=" * 70)
print("✅ Fix script completed!")
print("=" * 70)
print("\nTest the connection from ECS:")
print("  python3 scripts/test_database_connection.py")

