# 🐍 Literattus Django Frontend

Django-based frontend for the Literattus book club platform.

## 🏗️ Architecture

- **Framework**: Django 5.0+
- **Templates**: Django templates with Tailwind CSS
- **Backend Communication**: HTTP requests to FastAPI backend
- **Deployment**: Docker with Gunicorn

## 📁 Project Structure

```
frontend/
├── manage.py
├── requirements.txt
├── Dockerfile
├── literattus_frontend/      # Django project
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                      # Django apps
│   ├── core/                  # Home, dashboard
│   ├── books/                 # Book catalog
│   ├── clubs/                 # Club management
│   └── users/                 # Authentication
├── templates/                 # HTML templates
│   ├── base.html
│   ├── auth/
│   ├── main/
│   ├── books/
│   └── clubs/
└── static/                    # Static assets
    ├── css/
    ├── js/
    └── images/
```

## 🚀 Quick Start

### Local Development

```bash
cd frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Run development server
python manage.py runserver 0.0.0.0:8080
```

Visit: http://localhost:8080

### Docker

```bash
# From project root
docker-compose up frontend
```

## ⚙️ Configuration

Edit `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FASTAPI_BACKEND_URL=http://localhost:8000
```

## 🔗 FastAPI Backend Integration

The Django frontend communicates with the FastAPI backend via HTTP:

```python
import requests
from django.conf import settings

# Example: Fetch books
response = requests.get(f"{settings.FASTAPI_BACKEND_URL}/api/books/")
books = response.json()
```

## 📄 Templates

- `base.html` - Base template with navigation
- `auth/*` - Login, register, profile
- `main/*` - Home, dashboard, about
- `books/*` - Book catalog and details
- `clubs/*` - Club listings and details

## 🎨 Styling

Uses **Tailwind CSS** via CDN (for structure only).

For production, install django-tailwind:
```bash
pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build
```

## 🚢 Deployment

### Using Gunicorn

```bash
gunicorn --bind 0.0.0.0:8080 --workers 3 literattus_frontend.wsgi:application
```

### Using Docker

```bash
docker build -t literattus-frontend .
docker run -p 8080:8080 literattus-frontend
```

## 📚 Django Apps

### Core App
- Home page
- Dashboard
- About page

### Books App
- Book list
- Book details
- Book search

### Clubs App
- Club list
- Club details
- My clubs

### Users App
- Login
- Register
- Profile
- Logout

## 🔧 Development

```bash
# Create new app
python manage.py startapp app_name

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Shell
python manage.py shell
```

## 📖 Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [FastAPI Backend](../backend/README.md)
- [Project README](../README.md)

## ⚠️ Note

This is a **structure-only** implementation. Views contain TODOs for fetching data from the FastAPI backend. Complete implementation requires:

1. Implementing authentication flow with FastAPI
2. Adding HTTP client functions for API calls
3. Implementing form handling
4. Adding JavaScript for dynamic features
5. Completing all template pages

