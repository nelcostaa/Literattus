# 🐍 Literattus Python Backend

FastAPI-based backend for the Literattus book club platform.

## 🎯 Overview

This is the Python backend replacement for the original Next.js API routes. It provides a RESTful API built with FastAPI, SQLAlchemy ORM, and MySQL database support (including AWS RDS).

## 🏗️ Architecture

- **Framework**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0+ with Alembic migrations
- **Database**: MySQL 8.0+ (local or AWS RDS)
- **Authentication**: JWT with passlib (bcrypt)
- **Validation**: Pydantic V2
- **External APIs**: Google Books API integration

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                 # API route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── users.py        # User management
│   │   ├── books.py        # Book catalog & Google Books
│   │   └── clubs.py        # Club management
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── club.py
│   │   ├── club_member.py
│   │   ├── reading_progress.py
│   │   └── discussion.py
│   ├── schemas/            # Pydantic request/response schemas
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration management
│   │   ├── database.py     # Database connection
│   │   └── security.py     # Authentication & JWT
│   ├── services/           # Business logic services
│   │   └── google_books.py # Google Books API client
│   └── main.py             # FastAPI application entry point
├── tests/                  # Test suite
├── alembic/                # Database migrations
├── requirements.txt        # Python dependencies
└── env.example             # Environment variables template
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL 8.0+ (local or AWS RDS)
- Virtual environment (recommended)

### 1. Setup Virtual Environment

```bash
cd backend
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\\Scripts\\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp env.example .env
# Edit .env with your configuration
```

**Required environment variables:**

```env
# Database
DATABASE_URL=mysql+pymysql://user:REDACTED@host:3306/literattus
DB_HOST=localhost
DB_PORT=3306
DB_NAME=literattus
DB_USER=your_user
DB_PASSWORD=your_REDACTED

# Security
SECRET_KEY=your-secret-key-min-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Books API
GOOGLE_BOOKS_API_KEY=your-api-key

# CORS (Next.js frontend)
CORS_ORIGINS=["http://localhost:3000"]
```

### 4. Initialize Database

```bash
# Create all tables
python -c "from app.core.database import init_db; init_db()"

# Or use Alembic migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/api/redoc

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Registration

```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "REDACTED": "secure_REDACTED",
  "firstName": "John",
  "lastName": "Doe"
}
```

### Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "REDACTED": "secure_REDACTED"
}

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using Token

Include the token in the Authorization header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout (client-side token removal)

### Users
- `GET /api/users/` - List users (paginated)
- `GET /api/users/{user_id}` - Get user by ID
- `PUT /api/users/me` - Update current user profile
- `DELETE /api/users/me` - Deactivate account

### Books
- `GET /api/books/` - List books from catalog
- `GET /api/books/search?q=query` - Search Google Books
- `GET /api/books/{book_id}` - Get book by ID
- `GET /api/books/google/{google_books_id}` - Get book from Google Books
- `POST /api/books/` - Add book to catalog
- `PUT /api/books/{book_id}` - Update book
- `DELETE /api/books/{book_id}` - Delete book

### Clubs
- `GET /api/clubs/` - List clubs
- `GET /api/clubs/my-clubs` - Get user's clubs
- `GET /api/clubs/{club_id}` - Get club by ID
- `POST /api/clubs/` - Create new club
- `PUT /api/clubs/{club_id}` - Update club (admin only)
- `DELETE /api/clubs/{club_id}` - Delete club (owner only)
- `POST /api/clubs/{club_id}/join` - Join club
- `POST /api/clubs/{club_id}/leave` - Leave club
- `GET /api/clubs/{club_id}/members` - Get club members

## ☁️ AWS RDS MySQL Setup

### 1. Create RDS Instance

Follow these steps in AWS Console:

1. Go to **RDS** → **Create database**
2. Choose **MySQL 8.0**
3. Select **Free tier** or **Dev/Test** template
4. Configure:
   - **DB instance identifier**: `literattus-db`
   - **Master username**: `admin`
   - **Master REDACTED**: [strong REDACTED]
   - **DB instance class**: `db.t3.micro` (free tier eligible)
   - **Storage**: 20 GB SSD
   - **Public access**: **Yes** (for development)

5. Create security group allowing inbound on port **3306**:
   - Add your IP address
   - Add your friend's IP address

### 2. Get Connection Details

From RDS console, copy:
- **Endpoint**: `literattus-db.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com`
- **Port**: `3306`

### 3. Update .env

```env
DATABASE_URL=mysql+pymysql://admin:your_REDACTED@your-rds-endpoint.amazonaws.com:3306/literattus
DB_HOST=your-rds-endpoint.amazonaws.com
DB_PORT=3306
DB_NAME=literattus
DB_USER=admin
DB_PASSWORD=your_REDACTED
```

### 4. Initialize Database on RDS

```bash
# Connect and create database
mysql -h your-rds-endpoint.amazonaws.com -u admin -p

CREATE DATABASE literattus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Run migrations
alembic upgrade head
```

### 5. Import Existing Data (Optional)

If you have existing local data:

```bash
# Export from local
mysqldump -u local_user -p literattus > literattus_backup.sql

# Import to RDS
mysql -h your-rds-endpoint.amazonaws.com -u admin -p literattus < literattus_backup.sql
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Example Test

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "REDACTED": "testpass123",
        "firstName": "Test",
        "lastName": "User"
    })
    assert response.status_code == 201
    assert "email" in response.json()
```

## 🚀 Deployment

### Production Configuration

```env
APP_ENV=production
DEBUG=False
LOG_LEVEL=WARNING

# Use strong secret key
SECRET_KEY=<generate-strong-32+-char-key>

# Restrict CORS
CORS_ORIGINS=["https://yourdomain.com"]
```

### Using Uvicorn

```bash
# Production server with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn (Recommended for Production)

```bash
pip install gunicorn

gunicorn app.main:app \\
  --workers 4 \\
  --worker-class uvicorn.workers.UvicornWorker \\
  --bind 0.0.0.0:8000 \\
  --access-logfile - \\
  --error-logfile -
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔗 Connecting Frontend (Next.js)

The React frontend should point to the Python backend:

```typescript
// src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint: string, options?: RequestInit) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options?.headers,
    },
  });
  
  return response;
}
```

## 📝 Database Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "Add new field to user table"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current
```

## 🛠️ Development Tools

### Format Code

```bash
# Install
pip install black ruff

# Format
black app/
ruff check app/ --fix
```

### Type Checking

```bash
pip install mypy
mypy app/
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Run linters and tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the API docs at `/api/docs`
- Review logs in `logs/app.log`
- Open an issue on GitHub

