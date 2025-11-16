#!/usr/bin/env python3
"""
Test database connection from ECS task perspective.
Simulates the exact connection the backend would make.
"""

import sys
import pymysql
from urllib.parse import quote_plus

# Database credentials from task definition
DB_HOST = "literattus-1.cxukey2ou0s8.sa-east-1.rds.amazonaws.com"
DB_PORT = 3306
DB_USER = "admin"
DB_PASSWORD = "REDACTED"  # This is the hardcoded value in task definition
DB_NAME = "literattus"

def test_pymysql_connection():
    """Test direct pymysql connection (what backend uses)."""
    print("=" * 70)
    print("Testing Database Connection (Backend Perspective)")
    print("=" * 70)
    print(f"Host: {DB_HOST}")
    print(f"Port: {DB_PORT}")
    print(f"User: {DB_USER}")
    print(f"Database: {DB_NAME}")
    print(f"Password length: {len(DB_PASSWORD)}")
    print()
    
    # Test 1: Direct pymysql connection
    print("Test 1: Direct pymysql connection")
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
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print("✅ SUCCESS: Connection established")
        return True
    except pymysql.Error as e:
        print(f"❌ FAILED: {e}")
        return False

def test_sqlalchemy_url():
    """Test SQLAlchemy URL construction (what backend uses)."""
    print("\nTest 2: SQLAlchemy URL construction")
    try:
        from sqlalchemy import create_engine, text
        
        # Construct URL exactly as backend does
        REDACTED_encoded = quote_plus(DB_PASSWORD)
        database_url = f"mysql+pymysql://{DB_USER}:{REDACTED_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        print(f"URL: mysql+pymysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        engine = create_engine(database_url, pool_pre_ping=True, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ SUCCESS: SQLAlchemy connection established")
            return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_user_permissions():
    """Test if user can connect from different hosts."""
    print("\nTest 3: User host permissions")
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
        cursor.execute("SELECT user, host FROM mysql.user WHERE user = %s", (DB_USER,))
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"Found {len(users)} user entries:")
        for user, host in users:
            print(f"  - {user}@{host}")
        
        # Check if user can connect from any host
        has_wildcard = any(host == '%' for _, host in users)
        if has_wildcard:
            print("✅ User can connect from any host (%)")
        else:
            print("⚠️  User may only connect from specific hosts")
            print("   Consider: GRANT ALL PRIVILEGES ON literattus.* TO 'admin'@'%' IDENTIFIED BY 'REDACTED';")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    results = []
    results.append(("pymysql", test_pymysql_connection()))
    results.append(("sqlalchemy", test_sqlalchemy_url()))
    results.append(("permissions", test_user_permissions()))
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    if not all(success for _, success in results):
        sys.exit(1)

