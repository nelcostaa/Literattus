# 📚 Literattus - Your Book Club Social Hub

[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat&logo=next.js)](https://nextjs.org/)
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

### **Backend**
- **API**: Next.js API Routes with TypeScript
- **Database**: [MySQL](https://www.mysql.com/) with reliable performance and scalability
- **ORM**: [TypeORM](https://typeorm.io/) for type-safe database operations
- **Authentication**: JWT-based authentication system

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
├── 📂 src/
│   ├── 📂 app/                    # Next.js App Router
│   │   ├── 📂 (auth)/            # Authentication routes
│   │   │   ├── 📂 login/
│   │   │   ├── 📂 register/
│   │   │   └── 📂 forgot-REDACTED/
│   │   ├── 📂 (main)/            # Main application routes
│   │   │   ├── 📂 dashboard/
│   │   │   ├── 📂 clubs/
│   │   │   ├── 📂 books/
│   │   │   ├── 📂 profile/
│   │   │   └── 📂 settings/
│   │   ├── 📂 api/               # API Routes
│   │   │   ├── 📂 auth/
│   │   │   ├── 📂 books/
│   │   │   ├── 📂 clubs/
│   │   │   └── 📂 users/
│   │   ├── 📄 layout.tsx         # Root layout
│   │   ├── 📄 page.tsx           # Home page
│   │   └── 📄 globals.css        # Global styles
│   ├── 📂 components/            # React components
│   │   ├── 📂 ui/               # Reusable UI components
│   │   ├── 📂 features/         # Feature-specific components
│   │   └── 📂 layout/           # Layout components
│   ├── 📂 lib/                  # Utility libraries
│   │   ├── 📂 database/         # Database configuration
│   │   │   ├── 📂 entities/     # TypeORM entities
│   │   │   ├── 📂 migrations/   # Database migrations
│   │   │   └── 📄 data-source.ts
│   │   ├── 📂 utils/            # Utility functions
│   │   └── 📂 validations/      # Input validation schemas
│   └── 📂 types/                # TypeScript type definitions
├── 📂 scripts/                  # Python utility scripts
│   ├── 📄 requirements.txt      # Python dependencies
│   ├── 📄 db_setup.py          # Database setup utility
│   ├── 📄 google_books_sync.py # Google Books API sync
│   └── 📄 README.md            # Scripts documentation
├── 📂 public/                   # Static assets
│   ├── 📂 images/              # Image assets
│   ├── 📂 icons/               # Icon assets
│   └── 📂 uploads/             # User uploaded files
├── 📄 package.json             # Node.js dependencies
├── 📄 tsconfig.json            # TypeScript configuration
├── 📄 tailwind.config.ts       # Tailwind CSS configuration
├── 📄 next.config.mjs          # Next.js configuration
├── 📄 env.example              # Environment variables template
└── 📄 .gitignore               # Git ignore rules
```

## 🚀 Getting Started

### **Prerequisites**

- **Node.js** 18.17.0 or higher
- **npm** 9.0.0 or higher
- **MySQL Database** (local or cloud instance)
- **Python** 3.8+ (for utility scripts)

### **1. Clone the Repository**

```bash
git clone https://github.com/your-username/literattus.git
cd literattus
```

### **2. Install Dependencies**

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies for scripts
cd scripts
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### **3. Environment Configuration**

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env  # or your preferred editor
```

**Required Environment Variables:**

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=literattus
DB_USERNAME=your_db_user
DB_PASSWORD=your_db_REDACTED

# Google Books API
GOOGLE_BOOKS_API_KEY=your_google_books_api_key

# Authentication
JWT_SECRET=your_jwt_secret_key
NEXTAUTH_SECRET=your_nextauth_secret

# Application
NODE_ENV=development
APP_URL=http://localhost:3000
```

### **4. Database Setup**

```bash
# Run database setup script
python scripts/db_setup.py

# Generate and run migrations
npm run db:generate
npm run db:migrate
```

### **5. Start Development Server**

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to see your application running!

## 🛠️ Development Commands

### **Frontend Development**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run type-check   # Run TypeScript type checking
```

### **Database Management**
```bash
npm run db:generate  # Generate new migration
npm run db:migrate   # Run pending migrations
npm run db:revert    # Revert last migration
```

### **Code Quality**
```bash
npm run format       # Format code with Prettier
npm run format:check # Check code formatting
```

### **Python Scripts**
```bash
python scripts/db_setup.py         # Setup database
python scripts/google_books_sync.py # Sync Google Books data
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
