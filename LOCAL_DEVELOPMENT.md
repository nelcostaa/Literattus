# 🐍 Literattus Local MySQL Development Guide

## Quick Start (Docker Required)

### Prerequisites
- Docker and Docker Compose installed
- Python 3.10+ installed

### 1. Start MySQL Database
```bash
# Start MySQL container
docker-compose -f docker-compose.local.yml up -d

# Check if container is running
docker ps

# View logs
docker-compose -f docker-compose.local.yml logs mysql
```

### 2. Setup Database Schema
```bash
# Copy environment file
cp env.local .env

# Install Python dependencies
pip install mysql-connector-python python-dotenv loguru

# Run database setup
python scripts/db_setup.py
```

### 3. Test Database Connection
```bash
# Run interactive test script
python test.py
```

## Alternative: Local MySQL Installation

If Docker is not available, install MySQL locally:

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install mysql-server mysql-client
sudo mysql_secure_installation

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql
```

### macOS (with Homebrew)
```bash
brew install mysql
brew services start mysql
```

### Windows
Download MySQL Installer from https://dev.mysql.com/downloads/installer/

### Manual Database Setup
```sql
-- Connect as root
mysql -u root -p

-- Create database and user
CREATE DATABASE literattus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'literattus_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON literattus.* TO 'literattus_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

-- Connect as user and run schema
mysql -u literattus_user -p literattus < scripts/init.sql
```

## Database Connection Details

### Connection Parameters
- **Host:** localhost
- **Port:** 3306
- **Database:** literattus
- **Username:** literattus_user
- **Password:** password
- **Root Password:** rootpassword

### Connection String
```
mysql+pymysql://literattus_user:password@localhost:3306/literattus
```

## Using test.py Script

The `test.py` script provides an interactive interface for database operations:

### Features
- ✅ Test database connection
- ✅ Show all tables and record counts
- ✅ Display users, books, clubs
- ✅ Add sample data
- ✅ Interactive SQL mode
- ✅ Custom query execution

### Usage Examples
```bash
# Run the script
python test.py

# Choose options from menu:
# 1. Test database connection
# 2. Show all users
# 3. Show all books
# 4. Show all clubs
# 5. Add sample data
# 6. Interactive SQL mode
# 7. Run custom query
```

### Sample Queries
```sql
-- Show all users
SELECT id, email, first_name, last_name, created_at FROM users;

-- Show all books
SELECT id, title, authors, isbn FROM books;

-- Show clubs with creator info
SELECT c.name, u.email as created_by 
FROM clubs c 
JOIN users u ON c.created_by_id = u.id;

-- Add a new user
INSERT INTO users (email, password, first_name, last_name) 
VALUES ('new@test.com', 'hashed_password', 'New', 'User');

-- Update user status
UPDATE users SET is_active = 1 WHERE email = 'test@literattus.com';
```

## Cursor IDE Integration

### Database Extension Setup
1. Install "MySQL" extension in Cursor
2. Add connection:
   - Host: localhost
   - Port: 3306
   - Database: literattus
   - Username: literattus_user
   - Password: password

### Query Execution
- Use `Ctrl+Shift+P` → "MySQL: Execute Query"
- Or right-click in SQL file → "Execute Query"

## Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check if MySQL is running
docker ps  # For Docker
sudo systemctl status mysql  # For local MySQL

# Check port
netstat -tlnp | grep 3306
```

#### Authentication Failed
```bash
# Reset password
mysql -u root -p
ALTER USER 'literattus_user'@'localhost' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

#### Database Not Found
```bash
# Create database manually
mysql -u root -p
CREATE DATABASE literattus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Environment Variables
Make sure your `.env` file contains:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=literattus
DB_USER=literattus_user
DB_PASSWORD=password
MYSQL_ROOT_PASSWORD=rootpassword
```

## Next Steps

Once database is working:
1. ✅ Test with `python test.py`
2. ✅ Run queries in Cursor IDE
3. ✅ Start FastAPI backend: `cd backend && uvicorn app.main:app --reload`
4. ✅ Test API endpoints: http://localhost:8000/api/docs
5. ✅ Start Django frontend: `cd frontend && python manage.py runserver 8080`

## Production Deployment

For AWS deployment:
1. Use AWS RDS MySQL
2. Update connection strings
3. Use `backend/scripts/aws_rds_setup.py`
4. Configure security groups
5. Set up SSL certificates
