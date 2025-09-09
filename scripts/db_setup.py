#!/usr/bin/env python3
"""
Database setup and migration utility for Literattus.
This script helps with initial database setup and data seeding.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from loguru import logger

# Load environment variables from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / 'env.example')

def get_db_connection():
    """Get MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', '3306')),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD')
        )
        logger.info("Database connection established")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def main():
    """Main setup function."""
    logger.info("Starting Literattus database setup...")
    
    connection = get_db_connection()
    if not connection:
        sys.exit(1)
    
    logger.info("Database setup completed successfully")
    connection.close()

if __name__ == "__main__":
    main()
