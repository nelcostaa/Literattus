#!/usr/bin/env python3
"""
Simple MySQL test script for Literattus database.
Uses mysql-connector-python for direct database queries.
Perfect for testing connections and running queries from Cursor IDE.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'literattus'),
    'user': os.getenv('DB_USER', 'literattus_user'),
    'REDACTED': os.getenv('DB_PASSWORD', 'REDACTED'),
    'charset': 'utf8mb4',
    'autocommit': True
}

def connect_to_database():
    """Connect to MySQL database."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print(f"✅ Connected to MySQL database: {DB_CONFIG['database']}")
            print(f"   Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
            print(f"   User: {DB_CONFIG['user']}")
            return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def test_connection():
    """Test database connection and show basic info."""
    connection = connect_to_database()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Get database info
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"📊 MySQL Version: {version[0]}")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Tables in database: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Show table counts
        print("\n📈 Table Record Counts:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} records")
        
        cursor.close()
        return True
        
    except Error as e:
        print(f"❌ Error testing connection: {e}")
        return False
    finally:
        connection.close()
        print("🔌 Database connection closed")

def run_query(query, description=""):
    """Run a custom SQL query."""
    connection = connect_to_database()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        if description:
            print(f"\n🔍 {description}")
        
        cursor.execute(query)
        
        # Handle different query types
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            print(f"📊 Query Results ({len(results)} rows):")
            if results:
                # Print column headers
                print("   " + " | ".join(f"{col:15}" for col in columns))
                print("   " + "-" * (len(columns) * 18))
                
                # Print data rows
                for row in results:
                    print("   " + " | ".join(f"{str(val):15}" for val in row))
            else:
                print("   No results found")
            
            return results
        else:
            print(f"✅ Query executed successfully")
            return True
            
    except Error as e:
        print(f"❌ Error running query: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def show_users():
    """Show all users in the database."""
    query = """
    SELECT id, email, first_name, last_name, is_active, created_at 
    FROM users 
    ORDER BY created_at DESC
    """
    return run_query(query, "All Users")

def show_books():
    """Show all books in the database."""
    query = """
    SELECT id, title, authors, isbn, page_count, created_at 
    FROM books 
    ORDER BY created_at DESC
    """
    return run_query(query, "All Books")

def show_clubs():
    """Show all clubs in the database."""
    query = """
    SELECT c.id, c.name, c.description, u.email as created_by, c.created_at
    FROM clubs c
    JOIN users u ON c.created_by_id = u.id
    ORDER BY c.created_at DESC
    """
    return run_query(query, "All Clubs")

def add_sample_data():
    """Add some sample data for testing."""
    print("\n🌱 Adding sample data...")
    
    # Add a sample user
    user_query = """
    INSERT INTO users (email, REDACTED, first_name, last_name) 
    VALUES ('sample@test.com', 'hashed_REDACTED', 'Sample', 'User')
    """
    run_query(user_query, "Adding sample user")
    
    # Add a sample book
    book_query = """
    INSERT INTO books (title, authors, description, isbn) 
    VALUES ('Sample Book', 'Sample Author', 'A sample book for testing', '9780000000000')
    """
    run_query(book_query, "Adding sample book")

def interactive_mode():
    """Interactive mode for running custom queries."""
    print("\n🎯 Interactive Mode - Enter SQL queries (type 'exit' to quit)")
    print("Examples:")
    print("  SELECT * FROM users LIMIT 5;")
    print("  INSERT INTO books (title, authors) VALUES ('New Book', 'Author');")
    print("  UPDATE users SET is_active = 1 WHERE id = 1;")
    
    connection = connect_to_database()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        while True:
            query = input("\nSQL> ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                break
            
            if not query:
                continue
            
            try:
                cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    if results:
                        columns = [desc[0] for desc in cursor.description]
                        print("   " + " | ".join(f"{col:15}" for col in columns))
                        print("   " + "-" * (len(columns) * 18))
                        for row in results:
                            print("   " + " | ".join(f"{str(val):15}" for val in row))
                    else:
                        print("   No results found")
                else:
                    print("✅ Query executed successfully")
                    
            except Error as e:
                print(f"❌ Error: {e}")
    
    finally:
        cursor.close()
        connection.close()
        print("\n🔌 Interactive mode ended")

def main():
    """Main function with menu options."""
    print("🐍 Literattus MySQL Test Script")
    print("=" * 50)
    
    while True:
        print("\n📋 Choose an option:")
        print("1. Test database connection")
        print("2. Show all users")
        print("3. Show all books")
        print("4. Show all clubs")
        print("5. Add sample data")
        print("6. Interactive SQL mode")
        print("7. Run custom query")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            test_connection()
        elif choice == '2':
            show_users()
        elif choice == '3':
            show_books()
        elif choice == '4':
            show_clubs()
        elif choice == '5':
            add_sample_data()
        elif choice == '6':
            interactive_mode()
        elif choice == '7':
            query = input("Enter your SQL query: ").strip()
            if query:
                run_query(query, "Custom Query")
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
