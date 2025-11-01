#!/usr/bin/env python3
"""Test database connection for debugging."""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env
load_dotenv()

# Get credentials
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT", "3306")
db_user = os.getenv("DB_USER", "admin")
db_REDACTED = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME", "literattus")

print(f"Testing connection to: {db_user}@{db_host}:{db_port}/{db_name}")
print(f"Password length: {len(db_REDACTED) if db_REDACTED else 0}")

# Try direct mysql-connector-python (this works)
try:
    import mysql.connector
    conn = mysql.connector.connect(
        host=db_host,
        port=int(db_port),
        user=db_user,
        REDACTED=db_REDACTED,
        database=db_name
    )
    print("✓ mysql-connector-python: SUCCESS")
    conn.close()
except Exception as e:
    print(f"✗ mysql-connector-python: FAILED - {e}")

# Try SQLAlchemy with pymysql
try:
    from urllib.parse import quote_plus
    REDACTED_encoded = quote_plus(db_REDACTED)
    database_url = f"mysql+pymysql://{db_user}:{REDACTED_encoded}@{db_host}:{db_port}/{db_name}"
    print(f"\nTrying SQLAlchemy URL (REDACTED encoded): mysql+pymysql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    
    engine = create_engine(database_url, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ SQLAlchemy with pymysql: SUCCESS")
except Exception as e:
    print(f"✗ SQLAlchemy with pymysql: FAILED - {e}")

# Show what DATABASE_URL env var contains
database_url_env = os.getenv("DATABASE_URL")
print(f"\nDATABASE_URL from .env:")
print(f"  {database_url_env[:50]}...{database_url_env[-30:] if len(database_url_env) > 80 else database_url_env[50:]}")

