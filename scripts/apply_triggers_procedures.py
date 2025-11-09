#!/usr/bin/env python3
"""
Script to apply triggers and stored procedures to the Literattus database.
Reads and executes SQL from triggers_and_procedures.sql file.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_db_connection():
    """Get database connection from environment variables or .env file."""
    try:
        # Try to load from .env file first
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / 'backend' / '.env'
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass  # dotenv not available, use environment variables directly
    
    # Get database credentials from environment
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'REDACTED': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'literattus'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)

def execute_sql_file(connection, sql_file_path):
    """Execute SQL statements from a file."""
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by delimiter and execute each statement
        cursor = connection.cursor()
        
        # MySQL connector doesn't support DELIMITER, so we need to handle it manually
        # Split by DELIMITER statements and execute separately
        statements = []
        current_statement = []
        in_delimiter_block = False
        
        for line in sql_content.split('\n'):
            line_stripped = line.strip()
            
            # Handle DELIMITER statements
            if line_stripped.startswith('DELIMITER'):
                if '$$' in line_stripped:
                    in_delimiter_block = True
                else:
                    in_delimiter_block = False
                continue
            
            # Skip comments and empty lines
            if line_stripped.startswith('--') or not line_stripped:
                continue
            
            current_statement.append(line)
            
            # Check for statement end
            if not in_delimiter_block:
                if line_stripped.endswith(';'):
                    statements.append('\n'.join(current_statement))
                    current_statement = []
            else:
                if line_stripped.endswith('$$'):
                    statements.append('\n'.join(current_statement))
                    current_statement = []
        
        # Execute all statements
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    # Remove DELIMITER markers if present
                    statement = statement.replace('$$', ';')
                    # Execute multi-statement blocks
                    for result in cursor.execute(statement, multi=True):
                        if result.with_rows:
                            result.fetchall()
                    connection.commit()
                    print(f"✅ Executed statement {i}/{len(statements)}")
                except Error as e:
                    print(f"⚠️  Warning on statement {i}: {e}")
                    # Continue with next statement
        
        cursor.close()
        print(f"\n✅ Successfully applied {len(statements)} SQL statements")
        
    except FileNotFoundError:
        print(f"❌ SQL file not found: {sql_file_path}")
        sys.exit(1)
    except Error as e:
        print(f"❌ Error executing SQL: {e}")
        sys.exit(1)

def verify_installation(connection):
    """Verify that triggers and procedures were created successfully."""
    cursor = connection.cursor()
    
    print("\n📋 Verification:")
    print("-" * 50)
    
    # Check audit_log table
    try:
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        count = cursor.fetchone()[0]
        print(f"✅ audit_log table exists ({count} records)")
    except Error:
        print("❌ audit_log table not found")
    
    # Check triggers
    try:
        cursor.execute("""
            SELECT TRIGGER_NAME 
            FROM information_schema.TRIGGERS 
            WHERE TRIGGER_SCHEMA = DATABASE() 
            AND EVENT_OBJECT_TABLE = 'reading_progress'
        """)
        triggers = cursor.fetchall()
        if triggers:
            print(f"✅ Found {len(triggers)} trigger(s) on reading_progress:")
            for trigger in triggers:
                print(f"   - {trigger[0]}")
        else:
            print("❌ No triggers found on reading_progress")
    except Error as e:
        print(f"⚠️  Could not verify triggers: {e}")
    
    # Check stored procedure
    try:
        cursor.execute("""
            SELECT ROUTINE_NAME 
            FROM information_schema.ROUTINES 
            WHERE ROUTINE_SCHEMA = DATABASE() 
            AND ROUTINE_NAME = 'sp_get_user_reading_stats'
        """)
        proc = cursor.fetchone()
        if proc:
            print(f"✅ Stored procedure '{proc[0]}' exists")
        else:
            print("❌ Stored procedure not found")
    except Error as e:
        print(f"⚠️  Could not verify stored procedure: {e}")
    
    cursor.close()

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    sql_file = script_dir / 'triggers_and_procedures.sql'
    
    print("🚀 Applying Triggers and Stored Procedures")
    print("=" * 50)
    print(f"📄 SQL file: {sql_file}")
    
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        sys.exit(1)
    
    # Connect to database
    print("\n🔌 Connecting to database...")
    connection = get_db_connection()
    print("✅ Connected successfully")
    
    # Execute SQL file
    print(f"\n📝 Executing SQL from {sql_file.name}...")
    execute_sql_file(connection, sql_file)
    
    # Verify installation
    verify_installation(connection)
    
    # Close connection
    connection.close()
    print("\n✅ Done!")

if __name__ == '__main__':
    main()

