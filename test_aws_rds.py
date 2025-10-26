#!/usr/bin/env python3
"""
AWS RDS MySQL Test Script for Literattus
========================================
Interactive script to test and query the production AWS RDS database.
Uses credentials from backend/.env file.

Usage:
    python test_aws_rds.py              # Run menu interface
    python test_aws_rds.py --test       # Just test connection
    python test_aws_rds.py --query      # Interactive query mode
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from backend/.env
backend_env = Path(__file__).parent / "backend" / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
    print(f"✓ Loaded AWS RDS credentials from: {backend_env}")
else:
    print(f"❌ backend/.env not found at: {backend_env}")
    sys.exit(1)

# Database configuration from AWS RDS
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'literattus'),
    'user': os.getenv('DB_USER', 'admin'),
    'REDACTED': os.getenv('DB_PASSWORD'),
    'charset': 'utf8mb4',
    'autocommit': True,
    'connect_timeout': 10
}

def connect_to_database():
    """Connect to AWS RDS MySQL database."""
    try:
        print(f"\n🔌 Connecting to AWS RDS...")
        print(f"   Host: {DB_CONFIG['host']}")
        print(f"   Database: {DB_CONFIG['database']}")
        print(f"   User: {DB_CONFIG['user']}")
        
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Connected to AWS RDS MySQL Server version {db_info}")
            return connection
    except Error as e:
        print(f"❌ Error con1necting to AWS RDS: {e}")
        return None

def test_connection():
    """Test AWS RDS connection and show database info."""
    connection = connect_to_database()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Get database info
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"\n📊 MySQL Version: {version[0]}")
        
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print(f"📊 Current Database: {db_name[0]}")
        
        # Show all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📋 Tables ({len(tables)}):")
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        # Show table record counts
        print(f"\n📈 Table Record Counts:")
        total_records = 0
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   {table_name:20} : {count:5} records")
        
        print(f"\n📊 Total Records: {total_records}")
        
        cursor.close()
        return True
        
    except Error as e:
        print(f"❌ Error testing connection: {e}")
        return False
    finally:
        connection.close()
        print("\n🔌 Database connection closed")

def run_query(query, description="", show_description=True):
    """Run a custom SQL query and display results."""
    connection = connect_to_database()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        if description and show_description:
            print(f"\n{'='*70}")
            print(f"🔍 {description}")
            print(f"{'='*70}")
        
        cursor.execute(query)
        
        # Handle different query types
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if results:
                # Calculate column widths
                col_widths = [max(len(str(col)), 15) for col in columns]
                for row in results:
                    for i, val in enumerate(row):
                        col_widths[i] = max(col_widths[i], len(str(val)) if val is not None else 4)
                
                # Print column headers
                header = " | ".join(f"{col:<{col_widths[i]}}" for i, col in enumerate(columns))
                print(f"\n{header}")
                print("-" * len(header))
                
                # Print data rows
                for row in results:
                    row_str = " | ".join(
                        f"{str(val) if val is not None else 'NULL':<{col_widths[i]}}" 
                        for i, val in enumerate(row)
                    )
                    print(row_str)
                
                print(f"\n📊 {len(results)} row(s) returned")
            else:
                print("\n📭 No results found")
            
            return results
        else:
            affected = cursor.rowcount
            print(f"✅ Query executed successfully ({affected} row(s) affected)")
            return True
            
    except Error as e:
        print(f"❌ Error running query: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def show_all_users():
    """Show all users from AWS RDS."""
    query = """
    SELECT 
        id, 
        username,
        email, 
        CONCAT(first_name, ' ', last_name) as full_name,
        authorization,
        is_active, 
        DATE_FORMAT(created_at, '%Y-%m-%d') as created
    FROM users 
    ORDER BY created_at DESC
    LIMIT 20
    """
    return run_query(query, "All Users (from AWS RDS)")

def show_all_books():
    """Show all books from AWS RDS."""
    query = """
    SELECT 
        id as google_books_id,
        title, 
        author,
        isbn,
        page_count,
        DATE_FORMAT(published_date, '%Y-%m-%d') as published,
        DATE_FORMAT(created_at, '%Y-%m-%d') as added
    FROM books 
    ORDER BY created_at DESC
    LIMIT 20
    """
    return run_query(query, "All Books (from AWS RDS)")

def show_all_clubs():
    """Show all clubs from AWS RDS."""
    query = """
    SELECT 
        c.id, 
        c.name, 
        SUBSTRING(c.description, 1, 50) as description,
        CONCAT(u.first_name, ' ', u.last_name) as created_by,
        c.is_private,
        DATE_FORMAT(c.created_at, '%Y-%m-%d') as created
    FROM clubs c
    JOIN users u ON c.created_by_id = u.id
    ORDER BY c.created_at DESC
    """
    return run_query(query, "All Clubs (from AWS RDS)")

def show_club_books():
    """Show club-book relationships (NEW TABLE)."""
    query = """
    SELECT 
        cb.id,
        c.name as club_name,
        b.title as book_title,
        b.author,
        cb.status,
        DATE_FORMAT(cb.added_at, '%Y-%m-%d') as added
    FROM club_books cb
    JOIN clubs c ON cb.club_id = c.id
    JOIN books b ON cb.book_id = b.id
    ORDER BY cb.added_at DESC
    """
    return run_query(query, "Club-Book Relationships (NEW TABLE - resolves PDF feedback)")

def show_discussions_with_books():
    """Show discussions with book context (UPDATED TABLE)."""
    query = """
    SELECT 
        d.id,
        c.name as club_name,
        b.title as book_title,
        SUBSTRING(d.title, 1, 40) as discussion_title,
        CONCAT(u.first_name, ' ', u.last_name) as posted_by,
        DATE_FORMAT(d.created_at, '%Y-%m-%d') as posted
    FROM discussions d
    JOIN clubs c ON d.club_id = c.id
    JOIN books b ON d.book_id = b.id
    JOIN users u ON d.user_id = u.id
    ORDER BY d.created_at DESC
    LIMIT 10
    """
    return run_query(query, "Discussions with Book Context (resolves PDF feedback)")

def show_reading_progress():
    """Show user reading progress."""
    query = """
    SELECT 
        CONCAT(u.first_name, ' ', u.last_name) as reader,
        b.title as book,
        rp.status,
        rp.progress_percentage as progress,
        rp.rating,
        DATE_FORMAT(rp.started_at, '%Y-%m-%d') as started
    FROM reading_progress rp
    JOIN users u ON rp.user_id = u.id
    JOIN books b ON rp.book_id = b.id
    ORDER BY rp.updated_at DESC
    LIMIT 15
    """
    return run_query(query, "Reading Progress")

def show_club_members():
    """Show club membership details."""
    query = """
    SELECT 
        c.name as club_name,
        CONCAT(u.first_name, ' ', u.last_name) as member_name,
        cm.role,
        DATE_FORMAT(cm.joined_at, '%Y-%m-%d') as joined
    FROM club_members cm
    JOIN clubs c ON cm.club_id = c.id
    JOIN users u ON cm.user_id = u.id
    ORDER BY cm.joined_at DESC
    """
    return run_query(query, "Club Memberships")

def verify_schema_fixes():
    """Verify all PDF feedback issues are resolved."""
    print("\n" + "="*70)
    print("🔍 SCHEMA VERIFICATION - Checking PDF Feedback Fixes")
    print("="*70)
    
    connection = connect_to_database()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Test 1: club_books table exists
        print("\n1️⃣  Checking: club_books table exists...")
        cursor.execute("SHOW TABLES LIKE 'club_books'")
        result1 = cursor.fetchall()
        if result1:
            print("   ✅ club_books table exists (resolves 'cannot know which books in club')")
        else:
            print("   ❌ club_books table NOT FOUND")
        
        # Test 2: discussions have book_id
        print("\n2️⃣  Checking: discussions.book_id column exists...")
        cursor.execute("SHOW COLUMNS FROM discussions LIKE 'book_id'")
        result2 = cursor.fetchall()
        if result2:
            print("   ✅ discussions.book_id exists (resolves 'cannot know which book discussed')")
        else:
            print("   ❌ discussions.book_id NOT FOUND")
        
        # Test 3: reading_progress has club_id
        print("\n3️⃣  Checking: reading_progress.club_id column exists...")
        cursor.execute("SHOW COLUMNS FROM reading_progress LIKE 'club_id'")
        result3 = cursor.fetchall()
        if result3:
            print("   ✅ reading_progress.club_id exists (club reading challenges)")
        else:
            print("   ❌ reading_progress.club_id NOT FOUND")
        
        # Test 4: books.id is VARCHAR (Google Books ID)
        print("\n4️⃣  Checking: books.id is VARCHAR (Google Books ID)...")
        cursor.execute("SHOW COLUMNS FROM books WHERE Field = 'id'")
        result4 = cursor.fetchall()
        if result4 and 'varchar' in str(result4[0]).lower():
            print("   ✅ books.id is VARCHAR(12) - Google Books ID as PRIMARY KEY")
        else:
            print("   ❌ books.id is not VARCHAR")
        
        # Test 5: users have username field
        print("\n5️⃣  Checking: users.username column exists...")
        cursor.execute("SHOW COLUMNS FROM users LIKE 'username'")
        result5 = cursor.fetchall()
        if result5:
            print("   ✅ users.username exists (new field)")
        else:
            print("   ❌ users.username NOT FOUND")
        
        cursor.close()
        
    except Error as e:
        print(f"❌ Error during verification: {e}")
    finally:
        connection.close()
    
    print("\n" + "="*70)
    print("✅ Schema verification complete!")
    print("="*70)

def interactive_mode():
    """Interactive SQL query mode."""
    print("\n" + "="*70)
    print("🎯 INTERACTIVE MODE - AWS RDS Query Console")
    print("="*70)
    print("\nEnter SQL queries to run against AWS RDS")
    print("Commands:")
    print("  - Any SELECT/INSERT/UPDATE/DELETE query")
    print("  - 'exit' or 'quit' to leave")
    print("  - 'tables' to show all tables")
    print("  - 'help' for examples")
    print("\n" + "="*70)
    
    while True:
        try:
            query = input("\nAWS RDS> ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("👋 Exiting interactive mode")
                break
            
            if query.lower() == 'tables':
                run_query("SHOW TABLES", "All Tables")
                continue
            
            if query.lower() == 'help':
                print("\n📚 Example Queries:")
                print("  SELECT * FROM users LIMIT 5;")
                print("  SELECT * FROM books WHERE author LIKE '%Tolkien%';")
                print("  SELECT c.name, COUNT(cb.book_id) as book_count")
                print("    FROM clubs c")
                print("    LEFT JOIN club_books cb ON c.id = cb.club_id")
                print("    GROUP BY c.id;")
                continue
            
            # Ensure query ends with semicolon
            if not query.endswith(';'):
                query += ';'
            
            run_query(query, "Query Result")
            
        except KeyboardInterrupt:
            print("\n\n👋 Exiting interactive mode")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main_menu():
    """Main menu interface."""
    while True:
        print("\n" + "="*70)
        print("📊 LITERATTUS - AWS RDS DATABASE TEST SCRIPT")
        print("="*70)
        print("\nChoose an option:")
        print("  1. Test Connection & Show Database Info")
        print("  2. Show All Users")
        print("  3. Show All Books")
        print("  4. Show All Clubs")
        print("  5. Show Club-Book Relationships (NEW TABLE)")
        print("  6. Show Discussions with Book Context")
        print("  7. Show Reading Progress")
        print("  8. Show Club Memberships")
        print("  9. Verify Schema Fixes (PDF Feedback)")
        print(" 10. Interactive Query Mode")
        print("  0. Exit")
        print("="*70)
        
        choice = input("\nEnter choice (0-10): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            test_connection()
        elif choice == '2':
            show_all_users()
        elif choice == '3':
            show_all_books()
        elif choice == '4':
            show_all_clubs()
        elif choice == '5':
            show_club_books()
        elif choice == '6':
            show_discussions_with_books()
        elif choice == '7':
            show_reading_progress()
        elif choice == '8':
            show_club_members()
        elif choice == '9':
            verify_schema_fixes()
        elif choice == '10':
            interactive_mode()
        else:
            print("❌ Invalid choice. Please enter a number between 0-10.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            test_connection()
        elif sys.argv[1] == '--query':
            interactive_mode()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python test_aws_rds.py [--test|--query]")
    else:
        main_menu()

