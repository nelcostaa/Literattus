#!/usr/bin/env python3
"""
AWS RDS MySQL setup and migration script.
Helps setup database on AWS RDS and migrate data.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

console = Console()

# Load environment from parent directory
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")


def test_connection(host: str, port: str, user: str, REDACTED: str, database: str) -> bool:
    """Test MySQL connection."""
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            REDACTED=REDACTED,
            database=database,
            connect_timeout=10
        )
        
        if connection.is_connected():
            console.print("[green]✓[/green] Successfully connected to database!")
            connection.close()
            return True
            
    except Exception as e:
        console.print(f"[red]✗[/red] Connection failed: {e}")
        return False
    
    return False


def create_database(host: str, port: str, user: str, REDACTED: str, db_name: str) -> bool:
    """Create database if it doesn't exist."""
    try:
        import mysql.connector
        
        # Connect without database name
        connection = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            REDACTED=REDACTED,
            connect_timeout=10
        )
        
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {db_name}")
        
        console.print(f"[green]✓[/green] Database '{db_name}' is ready")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create database: {e}")
        return False


def export_local_database() -> str:
    """Export local database to SQL file."""
    console.print("\n[bold cyan]Exporting local database...[/bold cyan]")
    
    local_host = os.getenv("LOCAL_DB_HOST", "localhost")
    local_user = os.getenv("LOCAL_DB_USER", "root")
    local_REDACTED = os.getenv("LOCAL_DB_PASSWORD", "")
    local_db = os.getenv("LOCAL_DB_NAME", "literattus")
    
    backup_file = project_root / "backup_literattus.sql"
    
    cmd = [
        "mysqldump",
        f"-h{local_host}",
        f"-u{local_user}",
        f"-p{local_REDACTED}" if local_REDACTED else "",
        "--single-transaction",
        "--routines",
        "--triggers",
        local_db
    ]
    
    try:
        with open(backup_file, "w") as f:
            subprocess.run([c for c in cmd if c], stdout=f, check=True, stderr=subprocess.PIPE)
        
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        console.print(f"[green]✓[/green] Exported to {backup_file} ({size_mb:.2f} MB)")
        return str(backup_file)
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Export failed: {e.stderr.decode()}")
        return ""


def import_to_rds(backup_file: str, host: str, port: str, user: str, REDACTED: str, database: str) -> bool:
    """Import database backup to AWS RDS."""
    console.print(f"\n[bold cyan]Importing to AWS RDS...[/bold cyan]")
    
    cmd = f"mysql -h {host} -P {port} -u {user} -p{REDACTED} {database} < {backup_file}"
    
    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE)
        console.print(f"[green]✓[/green] Successfully imported to AWS RDS!")
        return True
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Import failed: {e.stderr.decode()}")
        return False


def main():
    """Main setup wizard."""
    console.print(Panel.fit(
        "[bold cyan]AWS RDS MySQL Setup Wizard[/bold cyan]\\n"
        "This script will help you setup and migrate your database to AWS RDS",
        border_style="cyan"
    ))
    
    # Check if AWS RDS credentials are configured
    rds_host = os.getenv("DB_HOST")
    rds_port = os.getenv("DB_PORT", "3306")
    rds_user = os.getenv("DB_USER")
    rds_REDACTED = os.getenv("DB_PASSWORD")
    rds_database = os.getenv("DB_NAME", "literattus")
    
    if not all([rds_host, rds_user, rds_REDACTED]):
        console.print("[yellow]⚠[/yellow] AWS RDS credentials not found in .env file")
        console.print("\\nPlease add these to your .env file:")
        console.print("""
DB_HOST=your-rds-endpoint.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=your_REDACTED
DB_NAME=literattus
        """)
        return
    
    # Display current configuration
    table = Table(title="AWS RDS Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Host", rds_host)
    table.add_row("Port", rds_port)
    table.add_row("User", rds_user)
    table.add_row("Password", "*" * len(rds_REDACTED))
    table.add_row("Database", rds_database)
    
    console.print(table)
    
    # Test connection
    console.print("\\n[bold]Step 1: Testing connection to AWS RDS...[/bold]")
    
    if not test_connection(rds_host, rds_port, rds_user, rds_REDACTED, "mysql"):
        console.print("[red]Cannot proceed without a valid connection[/red]")
        return
    
    # Create database
    console.print("\\n[bold]Step 2: Creating database...[/bold]")
    
    if not create_database(rds_host, rds_port, rds_user, rds_REDACTED, rds_database):
        return
    
    # Ask about data migration
    if Confirm.ask("\\n[bold]Do you want to migrate data from your local database?[/bold]"):
        backup_file = export_local_database()
        
        if backup_file and Confirm.ask("\\n[bold]Import this backup to AWS RDS?[/bold]"):
            import_to_rds(backup_file, rds_host, rds_port, rds_user, rds_REDACTED, rds_database)
    
    # Initialize schema
    if Confirm.ask("\\n[bold]Do you want to initialize database schema (create tables)?[/bold]"):
        console.print("\\n[cyan]Initializing database schema...[/cyan]")
        
        try:
            sys.path.insert(0, str(project_root))
            from app.core.database import init_db
            
            init_db()
            console.print("[green]✓[/green] Database schema initialized!")
            
        except Exception as e:
            console.print(f"[red]✗[/red] Schema initialization failed: {e}")
    
    # Success message
    console.print("\\n" + "="*60)
    console.print("[bold green]✓ AWS RDS Setup Complete![/bold green]")
    console.print("="*60)
    console.print("\\n[bold]Next steps:[/bold]")
    console.print("1. Start the FastAPI server: [cyan]uvicorn app.main:app --reload[/cyan]")
    console.print("2. Test the API: [cyan]http://localhost:8000/api/docs[/cyan]")
    console.print("3. Update your Next.js frontend to use: [cyan]http://localhost:8000[/cyan]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\\n[yellow]Setup cancelled by user[/yellow]")
        sys.exit(0)

