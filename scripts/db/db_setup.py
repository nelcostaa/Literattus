#!/usr/bin/env python3
"""
Enhanced database setup and testing utility for Literattus.
This script helps with initial database setup, schema creation, and testing.
Connects to AWS RDS database using credentials from backend/.env
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from loguru import logger

# Load environment variables from backend/.env
project_root = Path(__file__).parent.parent
backend_env = project_root / 'backend' / '.env'
if not backend_env.exists():
    logger.error(f"Backend .env file not found at: {backend_env}")
    sys.exit(1)
load_dotenv(backend_env)
logger.info(f"Loaded configuration from: {backend_env}")

def get_db_connection(use_root=False):
    """Get MySQL database connection to AWS RDS."""
    # Validate required environment variables
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return None
    
    try:
        if use_root:
            # Use admin/root connection for AWS RDS admin operations
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', '3306')),
                user=os.getenv('DB_USER'),  # AWS RDS admin user
                REDACTED=os.getenv('DB_PASSWORD')
            )
        else:
            # Use regular user connection
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', '3306')),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                REDACTED=os.getenv('DB_PASSWORD')
            )
        
        logger.info(f"Database connection established ({'root' if use_root else 'user'})")
        return connection
    except Error as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def create_database():
    """Create the literattus database if it doesn't exist on AWS RDS."""
    logger.warning("Note: On AWS RDS, database creation typically requires master/admin privileges")
    connection = get_db_connection(use_root=True)
    if not connection:
        logger.error("Cannot create database without admin connection")
        return False
    
    try:
        cursor = connection.cursor()
        db_name = os.getenv('DB_NAME')
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        logger.success(f"Database '{db_name}' created/verified on AWS RDS")
        
        # Note: AWS RDS user creation is typically done via RDS console or AWS CLI
        # This script assumes the user already exists
        logger.info("AWS RDS user management should be done via AWS Console or CLI")
        
        cursor.close()
        return True
        
    except Error as e:
        logger.error(f"Failed to create database/user: {e}")
        return False
    finally:
        connection.close()

def test_connection():
    """Test database connection and show basic info."""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Get database info
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        logger.info(f"MySQL Version: {version[0]}")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        logger.info(f"Tables in database: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            logger.info(f"  - {table_name}: {count} records")
        
        cursor.close()
        return True
        
    except Error as e:
        logger.error(f"Error testing connection: {e}")
        return False
    finally:
        connection.close()

def run_sql_file(sql_file_path):
    """Run SQL commands from a file."""
    if not os.path.exists(sql_file_path):
        logger.error(f"SQL file not found: {sql_file_path}")
        return False
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
                # Consume any results to prevent "Unread result found" error
                if cursor.description:
                    cursor.fetchall()
        
        connection.commit()
        logger.success(f"SQL file executed successfully: {sql_file_path}")
        cursor.close()
        return True
        
    except Error as e:
        logger.error(f"Error executing SQL file: {e}")
        return False
    finally:
        connection.close()

def main():
    """Main setup function."""
    logger.info("Starting Literattus database setup...")
    
    # Step 1: Create database and user
    logger.info("Step 1: Creating database and user...")
    if not create_database():
        logger.error("Failed to create database")
        sys.exit(1)
    
    # Step 2: Run schema initialization
    logger.info("Step 2: Running schema initialization...")
    init_sql_path = project_root / 'scripts' / 'init.sql'
    if not run_sql_file(init_sql_path):
        logger.error("Failed to run schema initialization")
        sys.exit(1)
    
    # Step 3: Test connection
    logger.info("Step 3: Testing connection...")
    if not test_connection():
        logger.error("Failed to test connection")
        sys.exit(1)
    
    logger.success("Database setup completed successfully!")
    logger.info("You can now use test.py to interact with the database")

if __name__ == "__main__":
    main()
