# 🚀 Literattus - Quick Start Guide

**Get up and running in 5 minutes!**

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version  # or python3 --version

# Check Node.js version (need 18.17+)
node --version

# Check MySQL installation
mysql --version
```

## 🎯 Option 1: Local Development (Fastest)

### Step 1: Clone & Setup
```bash
git clone <your-repo-url>
cd Literattus
```

### Step 2: Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your MySQL credentials:
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_REDACTED
# DB_NAME=literattus
```

### Step 3: Database Setup
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE literattus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Initialize tables
python -c "from app.core.database import init_db; init_db()"
```

### Step 4: Start Backend
```bash
uvicorn app.main:app --reload --port 8000
```

✅ Backend running at http://localhost:8000/api/docs

### Step 5: Start Frontend (New Terminal)
```bash
cd ..  # Back to project root
npm install
npm run dev
```

✅ Frontend running at http://localhost:3000

---

## ☁️ Option 2: AWS RDS Setup

### Step 1: Create RDS Instance
1. Go to AWS Console → RDS
2. Click "Create database"
3. Choose MySQL 8.0
4. Select Free tier template
5. Set:
   - DB identifier: `literattus-db`
   - Master username: `admin`
   - Master REDACTED: [strong REDACTED]
   - Instance: `db.t3.micro`
6. Public access: **Yes**
7. Create database (wait 5-10 minutes)

### Step 2: Configure Security Group
1. Go to your RDS instance
2. Click on the VPC security group
3. Edit inbound rules
4. Add rule:
   - Type: MySQL/Aurora
   - Port: 3306
   - Source: My IP (automatically detected)

### Step 3: Setup Backend with RDS
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and edit environment
cp env.example .env

# Edit .env with RDS credentials:
# DB_HOST=literattus-db.xxxxxxxxx.us-east-1.rds.amazonaws.com
# DB_USER=admin
# DB_PASSWORD=your_rds_REDACTED
# DB_NAME=literattus
```

### Step 4: Run Setup Wizard
```bash
python scripts/aws_rds_setup.py

# Follow prompts to:
# ✓ Test connection
# ✓ Create database
# ✓ Migrate data (if needed)
# ✓ Initialize schema
```

### Step 5: Start Services
```bash
# Terminal 1: Backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd ..
npm install
npm run dev
```

---

## 🐳 Option 3: Docker (Easiest)

### Run Everything with Docker
```bash
cd backend
docker-compose up -d

# Backend: http://localhost:8000
# MySQL: localhost:3306
```

### Start Frontend Separately
```bash
cd ..
npm install
npm run dev

# Frontend: http://localhost:3000
```

---

## 🧪 Test Your Setup

### 1. Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status":"healthy","app_name":"Literattus",...}
```

### 2. Test API Docs
Visit: http://localhost:8000/api/docs

You should see interactive API documentation (Swagger UI)

### 3. Test Frontend
Visit: http://localhost:3000

You should see the Literattus homepage

### 4. Test Registration
1. Go to http://localhost:3000/register
2. Create a test account
3. Check if you're redirected to dashboard

---

## 🔧 Common Issues

### Issue: "Module not found" in Python
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Can't connect to MySQL"
```bash
# Check MySQL is running
mysql -u root -p

# Check credentials in backend/.env match your MySQL
```

### Issue: "Port 8000 already in use"
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Issue: Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Update frontend .env
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env
```

---

## 📚 Next Steps

1. **Read the docs**: Check `backend/README.md` for detailed backend docs
2. **Explore API**: http://localhost:8000/api/docs
3. **Add your Google Books API key** to `backend/.env`
4. **Invite your friend** - Share AWS RDS credentials securely

---

## 🆘 Need Help?

- Check `README.md` for detailed documentation
- Review `backend/README.md` for API documentation
- Open an issue on GitHub
- Check logs in `backend/logs/app.log`

**Happy coding! 🎉**

