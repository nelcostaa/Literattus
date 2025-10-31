# Literattus Development Guide

Quick reference for developing on Literattus.

## 🚀 Quick Start

### After Booting Your PC
```bash
cd /home/nelso/Documents/Literattus
./dev start
```

### Common Commands
```bash
./dev start          # Start services
./dev start --force  # Force start (kills stuck processes)
./dev stop           # Stop services
./dev restart        # Restart services
./dev status         # Check status
./dev logs           # View all logs
./dev logs backend   # View backend logs only
./dev logs frontend  # View frontend logs only
```

## 🌐 Access Points

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000/api/docs
- **Database**: AWS RDS (sa-east-1)

## 🎨 Making CSS Changes

1. Edit `frontend/static/css/main.css`
2. Save the file
3. Refresh browser (`Ctrl+R`)
4. Changes appear immediately (Django hot-reload)

If changes don't appear:
- Hard refresh: `Ctrl+Shift+R`
- Restart frontend: `./dev restart`

## 📂 Project Structure

```
Literattus/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── tests/        # Backend tests
│   └── .env          # Backend config (AWS RDS credentials)
├── frontend/         # Django frontend
│   ├── apps/         # Django apps (core, books, clubs, users)
│   ├── templates/    # HTML templates
│   └── static/       # CSS, JS, images
├── scripts/          # Management scripts
│   ├── start         # Start services
│   ├── stop          # Stop services
│   ├── status        # Show status
│   ├── logs          # View logs
│   └── README.md     # Detailed script documentation
└── dev               # Main CLI helper
```

## 🔧 Troubleshooting

### Port Already in Use
```bash
./dev start --force
```

### Services Not Responding
```bash
./dev logs           # Check for errors
./dev restart        # Restart everything
```

### Docker Not Running
```bash
sudo systemctl start docker
```

### CSS Changes Not Showing
```bash
# Hard refresh
Ctrl + Shift + R

# Or restart frontend
./dev restart
```

## 📝 Database

- **Type**: MySQL 8.0
- **Location**: AWS RDS (sa-east-1)
- **Credentials**: `backend/.env`
- **Test Script**: `scripts/test_aws_rds.py`

All services connect to AWS RDS. No local database needed.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Test AWS RDS Connection
```bash
python scripts/test_aws_rds.py --test
```

## 📖 Additional Documentation

- **Scripts**: See `scripts/README.md` for detailed script documentation
- **Backend**: See `backend/README.md` for backend-specific docs
- **Frontend**: See `frontend/README.md` for frontend-specific docs

