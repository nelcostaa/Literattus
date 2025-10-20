# 📚 Literattus - Your Book Club Social Hub

[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat&logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4+-blue?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue?style=flat&logo=mysql)](https://www.mysql.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-38B2AC?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Literattus** is a modern, full-stack SaaS platform designed to be the ultimate social hub for book clubs and reading communities. Built with cutting-edge technologies, it provides a comprehensive solution for readers to catalog their books, create and manage book clubs, engage in discussions, and track their reading progress.

## ✨ Features

### 📖 **Personal Reading Management**
- **Digital Library**: Catalog your personal book collection
- **Reading Progress**: Track your current reads and set reading goals
- **Book Discovery**: Discover new books through Google Books API integration
- **Reading Statistics**: Visualize your reading habits and achievements

### 👥 **Book Club Management**
- **Create & Join Clubs**: Start your own book club or join existing communities
- **Member Management**: Invite friends and manage club memberships
- **Book Selection**: Democratic voting system for choosing the next club read
- **Discussion Forums**: Engage in rich discussions about books and chapters

### 🎯 **Social Features**
- **Community Interaction**: Connect with fellow book enthusiasts
- **Reviews & Ratings**: Share your thoughts and discover what others are reading
- **Reading Challenges**: Participate in community reading challenges
- **Recommendations**: Get personalized book recommendations

### 🔧 **Advanced Functionality**
- **Multi-format Support**: Support for physical books, eBooks, and audiobooks
- **Progress Tracking**: Chapter-by-chapter progress monitoring
- **Notification System**: Stay updated on club activities and discussions
- **Mobile Responsive**: Fully responsive design for all devices

## 🏗️ Architecture & Tech Stack

### **Frontend**
- **Framework**: [Next.js 14+](https://nextjs.org/) with App Router
- **Language**: [TypeScript](https://www.typescriptlang.org/) in strict mode
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) utility-first approach
- **UI Components**: Custom component library built with Radix UI primitives

### **Backend** 🐍
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- **Language**: [Python 3.11+](https://www.python.org/)
- **Database**: [MySQL 8.0+](https://www.mysql.com/) with AWS RDS support
- **ORM**: [SQLAlchemy 2.0+](https://www.sqlalchemy.org/) for database operations
- **Authentication**: JWT with passlib (bcrypt) for secure REDACTED hashing
- **Validation**: [Pydantic V2](https://docs.pydantic.dev/) for request/response validation
- **API Documentation**: Auto-generated Swagger UI and ReDoc

### **External Integrations**
- **Google Books API**: Rich book metadata and cover images
- **Email Service**: SMTP integration for notifications
- **File Upload**: Secure file handling for user avatars and club images

### **Development Tools**
- **Linting**: ESLint with TypeScript rules
- **Formatting**: Prettier with Tailwind CSS plugin
- **Type Checking**: Strict TypeScript configuration
- **Python Scripts**: Utility scripts for data management and API synchronization

## 📁 Project Structure

```
literattus/
├── 📂 backend/                  # Python FastAPI Backend
│   ├── 📂 app/
│   │   ├── 📂 api/             # API route handlers
│   │   │   ├── 📄 auth.py      # Authentication endpoints
│   │   │   ├── 📄 users.py     # User management
│   │   │   ├── 📄 books.py     # Books & Google Books API
│   │   │   └── 📄 clubs.py     # Club management
│   │   ├── 📂 models/          # SQLAlchemy ORM models
│   │   │   ├── 📄 user.py
│   │   │   ├── 📄 book.py
│   │   │   ├── 📄 club.py
│   │   │   ├── 📄 club_member.py
│   │   │   ├── 📄 reading_progress.py
│   │   │   └── 📄 discussion.py
│   │   ├── 📂 schemas/         # Pydantic validation schemas
│   │   ├── 📂 core/            # Core functionality
│   │   │   ├── 📄 config.py    # Configuration
│   │   │   ├── 📄 database.py  # Database connection
│   │   │   └── 📄 security.py  # Auth & JWT
│   │   ├── 📂 services/        # Business logic
│   │   │   └── 📄 google_books.py
│   │   └── 📄 main.py          # FastAPI app entry point
│   ├── 📂 tests/               # Pytest test suite
│   ├── 📂 scripts/             # Setup & migration scripts
│   ├── 📄 requirements.txt     # Python dependencies
│   ├── 📄 Dockerfile           # Docker configuration
│   └── 📄 README.md            # Backend documentation
├── 📂 src/                      # Next.js Frontend
│   ├── 📂 app/                 # Next.js App Router
│   │   ├── 📂 (auth)/          # Authentication pages
│   │   │   ├── 📂 login/
│   │   │   ├── 📂 register/
│   │   │   └── 📂 forgot-REDACTED/
│   │   ├── 📂 (main)/          # Main application pages
│   │   │   ├── 📂 dashboard/
│   │   │   ├── 📂 clubs/
│   │   │   ├── 📂 books/
│   │   │   ├── 📂 profile/
│   │   │   └── 📂 settings/
│   │   ├── 📄 layout.tsx       # Root layout
│   │   ├── 📄 page.tsx         # Home page
│   │   └── 📄 globals.css      # Global styles
│   ├── 📂 components/          # React components
│   │   ├── 📂 ui/              # Reusable UI components
│   │   ├── 📂 features/        # Feature components
│   │   └── 📂 layout/          # Layout components
│   ├── 📂 lib/                 # Utility libraries
│   │   ├── 📂 utils/           # Helper functions
│   │   └── 📂 api/             # API client for backend
│   └── 📂 types/               # TypeScript definitions
├── 📂 scripts/                 # Utility scripts
│   ├── 📄 requirements.txt     # Python dependencies
│   ├── 📄 db_setup.py          # Database utilities
│   └── 📄 google_books_sync.py # Google Books sync
├── 📂 public/                  # Static assets
│   ├── 📂 images/
│   ├── 📂 icons/
│   └── 📂 uploads/
├── 📄 package.json             # Node.js dependencies
├── 📄 tsconfig.json            # TypeScript configuration
├── 📄 tailwind.config.ts       # Tailwind CSS configuration
├── 📄 next.config.mjs          # Next.js configuration
└── 📄 env.example              # Environment template
```

## 🚀 Getting Started

### **Prerequisites**

- **Python** 3.11+ (for backend)
- **Node.js** 18.17.0+ (for frontend)
- **npm** 9.0.0+ (for frontend)
- **MySQL** 8.0+ (local or AWS RDS)
- **Git** for version control

### **1. Clone the Repository**

```bash
git clone https://github.com/your-username/literattus.git
cd literattus
```

### **2. Install Dependencies**

**Backend (Python FastAPI):**
```bash
cd backend
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

**Frontend (Next.js):**
```bash
cd ..  # Back to project root
npm install
```

### **3. Environment Configuration**

**Backend Configuration:**
```bash
cd backend
cp env.example .env
# Edit backend/.env with your settings
```

**Required Backend Variables:**
```env
# Database (Local or AWS RDS)
DATABASE_URL=mysql+pymysql://user:REDACTED@host:3306/literattus
DB_HOST=localhost  # or your-rds-endpoint.amazonaws.com
DB_PORT=3306
DB_NAME=literattus
DB_USER=your_user
DB_PASSWORD=your_REDACTED

# Security
SECRET_KEY=your-secret-key-min-32-characters-for-jwt
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Books API
GOOGLE_BOOKS_API_KEY=your_google_books_api_key

# CORS (Next.js frontend URL)
CORS_ORIGINS=["http://localhost:3000"]
```

**Frontend Configuration:**
```bash
cd ..  # Back to project root
cp env.example .env
# Edit .env with frontend settings
```

**Required Frontend Variables:**
```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Other Next.js settings
NODE_ENV=development
APP_URL=http://localhost:3000
```

### **4. Database Setup**

**Option A: Local MySQL**
```bash
# Create database
mysql -u root -p
CREATE DATABASE literattus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Initialize tables (from backend directory)
cd backend
python -c "from app.core.database import init_db; init_db()"
```

**Option B: AWS RDS MySQL**
```bash
# Use the interactive setup wizard
cd backend
python scripts/aws_rds_setup.py

# Follow the prompts to:
# - Test connection
# - Create database
# - Migrate existing data (optional)
# - Initialize schema
```

### **5. Start Development Servers**

**Terminal 1 - Backend (FastAPI):**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend will run at: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

**Terminal 2 - Frontend (Next.js):**
```bash
# From project root
npm run dev
```
Frontend will run at: http://localhost:3000

🎉 **Visit http://localhost:3000 to use the application!**

## 🛠️ Development Commands

### **Backend (Python FastAPI)**
```bash
# Start development server
cd backend
uvicorn app.main:app --reload --port 8000

# Run tests
pytest
pytest --cov=app --cov-report=html

# Code quality
black app/              # Format code
ruff check app/ --fix   # Lint and fix

# Database migrations (Alembic)
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1
```

### **Frontend (Next.js)**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run type-check   # Run TypeScript type checking
npm run format       # Format code with Prettier
```

### **Utility Scripts**
```bash
# AWS RDS setup wizard
python backend/scripts/aws_rds_setup.py

# Google Books sync (legacy)
python scripts/google_books_sync.py
```

### **Docker (Full Stack)**
```bash
# Start both backend and database
cd backend
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🗃️ Database Schema

The application uses a robust MySQL database schema with the following main entities:

- **Users**: User accounts and profiles
- **Books**: Book catalog with Google Books integration
- **Clubs**: Book club information and settings
- **ClubMembers**: Club membership with roles and permissions
- **ReadingProgress**: Individual reading progress tracking
- **Discussions**: Club discussions and comments

## 🔌 API Documentation

### **Authentication Endpoints**
- `POST /api/auth` - User authentication
- `GET /api/auth` - Get authentication status

### **Books Endpoints**
- `GET /api/books` - Get books catalog
- `POST /api/books` - Add new book

### **Clubs Endpoints**
- `GET /api/clubs` - Get book clubs
- `POST /api/clubs` - Create new club

### **Users Endpoints**
- `GET /api/users` - Get user profiles
- `PUT /api/users` - Update user profile

## 🎨 UI Components

The application features a comprehensive component library:

### **Base Components**
- `Button` - Versatile button component with multiple variants
- `Card` - Container component for content organization
- `Input` - Form input components with validation
- `Modal` - Overlay components for dialogs and popups

### **Feature Components**
- `BookCard` - Display book information and actions
- `ClubCard` - Show club details and member information
- `ReadingProgress` - Visual progress indicators
- `DiscussionThread` - Threaded discussion interface

## 🤝 Contributing

We welcome contributions to Literattus! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### **Development Guidelines**

- Follow the established TypeScript and React patterns
- Use Tailwind CSS for all styling
- Write comprehensive tests for new features
- Ensure all linting and type checking passes
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) for the amazing React framework
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework
- [TypeORM](https://typeorm.io/) for the excellent TypeScript ORM
- [Google Books API](https://developers.google.com/books) for book data
- [Radix UI](https://www.radix-ui.com/) for accessible component primitives

**Happy Reading! 📚✨**

*Built with ❤️ by the Literattus team*
