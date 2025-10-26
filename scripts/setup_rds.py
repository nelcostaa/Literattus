#!/usr/bin/env python3
"""
Direct AWS RDS setup script using admin credentials.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from loguru import logger

# Load environment variables
project_root = Path(__file__).parent.parent
backend_env = project_root / "backend" / ".env"

if backend_env.exists():
    load_dotenv(backend_env)
    logger.info(f"Loaded environment from {backend_env}")
else:
    logger.error(f"Environment file not found: {backend_env}")
    sys.exit(1)

# Get database credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "literattus")

logger.info(f"Connecting to RDS: {DB_USER}@{DB_HOST}:{DB_PORT}")

def execute_sql_file(connection, sql_file_path: Path):
    """Execute SQL file with proper statement separation."""
    logger.info(f"Executing SQL file: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    cursor = connection.cursor()
    
    # Remove comments and split by semicolon
    lines = sql_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove comments
        if line.strip().startswith('--'):
            continue
        cleaned_lines.append(line)
    
    sql_content = '\n'.join(cleaned_lines)
    
    # Split by semicolon (this preserves multi-line statements)
    statements = sql_content.split(';')
    
    successful = 0
    for i, statement in enumerate(statements, 1):
        statement = statement.strip()
        if not statement:
            continue
            
        try:
            cursor.execute(statement)
            # Consume any result sets
            try:
                while cursor.nextset():
                    pass
            except:
                pass
            successful += 1
            
            # Log CREATE TABLE statements
            if statement.upper().startswith('CREATE TABLE'):
                table_name = statement.split('CREATE TABLE IF NOT EXISTS')[1].split('(')[0].strip() if 'IF NOT EXISTS' in statement.upper() else statement.split('CREATE TABLE')[1].split('(')[0].strip()
                logger.info(f"  ✓ Created table: {table_name}")
                
        except Exception as e:
            # Only log as error if it's not a benign warning
            if 'doesn\'t exist' not in str(e):
                logger.error(f"Statement {i} error: {e}")
                logger.debug(f"Statement: {statement[:200]}...")
    
    connection.commit()
    cursor.close()
    logger.success(f"SQL file executed successfully ({successful} statements)")


def main():
    """Main setup function."""
    logger.info("=" * 70)
    logger.info("AWS RDS Database Setup")
    logger.info("=" * 70)
    
    # Step 1: Connect to RDS
    logger.info("Step 1: Connecting to AWS RDS...")
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            REDACTED=DB_PASSWORD,
            connect_timeout=10
        )
        logger.success("✓ Connected to RDS successfully")
    except Exception as e:
        logger.error(f"✗ Failed to connect: {e}")
        sys.exit(1)
    
    # Step 2: Create database if it doesn't exist
    logger.info("Step 2: Creating database...")
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {DB_NAME}")
        logger.success(f"✓ Database '{DB_NAME}' is ready")
    except Exception as e:
        logger.error(f"✗ Failed to create database: {e}")
        connection.close()
        sys.exit(1)
    finally:
        cursor.close()
    
    # Step 3: Execute init.sql
    logger.info("Step 3: Executing init.sql schema...")
    init_sql = project_root / "scripts" / "init.sql"
    
    if not init_sql.exists():
        logger.error(f"✗ init.sql not found: {init_sql}")
        connection.close()
        sys.exit(1)
    
    try:
        execute_sql_file(connection, init_sql)
        logger.success("✓ Database schema initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize schema: {e}")
        connection.close()
        sys.exit(1)
    
    # Step 4: Verify tables
    logger.info("Step 4: Verifying database schema...")
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        logger.success(f"✓ Found {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            logger.info(f"  - {table[0]}: {count} records")
    except Exception as e:
        logger.error(f"✗ Failed to verify tables: {e}")
    finally:
        cursor.close()
    
    # Close connection
    connection.close()
    
    logger.info("=" * 70)
    logger.success("✓ AWS RDS Setup Complete!")
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info("1. cd backend")
    logger.info("2. uvicorn app.main:app --reload --port 8000")
    logger.info("3. Visit: http://localhost:8000/api/docs")


if __name__ == "__main__":
    main()

