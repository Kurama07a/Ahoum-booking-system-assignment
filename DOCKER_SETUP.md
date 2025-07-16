# Docker Quick Start Guide 🐳

## TL;DR - Just Run It!

```bash
# Clone the repo
git clone <repository-url>
cd booking-system

# Run everything (production-ready)
docker-compose up -d

# Or run for development
docker-compose -f docker-compose.dev.yml up -d
```

That's it! The app will be running at `http://localhost:3000` 🎉

## What Gets Started

When you run `docker-compose up`, you get:

| Service | Port | What it does |
|---------|------|-------------|
| **Frontend** | :3000 | React app (main UI) |
| **Backend** | :5000 | API server |
| **CRM Service** | :5001 | Booking notifications |
| **Notification Service** | :5002 | Real-time messages |
| **Email Service** | :5003 | Sends emails |
| **Database** | :5432 | PostgreSQL |
| **Nginx** | :80 | Reverse proxy |

## Different Modes

### 🚀 Production Mode (Default)
```bash
docker-compose up -d
```
- Uses PostgreSQL database
- Optimized builds
- Nginx reverse proxy
- Strong security tokens

### 🔧 Development Mode
```bash
docker-compose -f docker-compose.dev.yml up -d
```
- Uses SQLite (simpler)
- Live code reloading
- Debug mode enabled
- Weaker dev tokens

### 🏗️ Backend Only
```bash
docker-compose -f docker-compose.backend.yml up -d
```
- Just the API services
- No frontend
- Good for API testing

## Quick Commands

### Start Everything
```bash
docker-compose up -d
```

### Stop Everything
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Clean Start (Reset Database)
```bash
docker-compose down -v
docker-compose up -d
```

## First Time Setup

1. **Install Docker** (if you haven't)
   - Windows/Mac: Docker Desktop
   - Linux: `sudo apt install docker.io docker-compose`

2. **Clone & Run**
   ```bash
   git clone <repo>
   cd booking-system
   docker-compose up -d
   ```

3. **Wait for services to start** (about 30 seconds)

4. **Open your browser** → `http://localhost:3000`

## Default Accounts

The system creates these accounts automatically:

**Facilitator Account:**
- Email: `facilitator@example.com`
- Password: `password123`
- Role: Can create sessions

**Sample Sessions:**
- Morning Meditation (1-hour session)
- Weekend Retreat (2-day retreat)

## Environment Variables

### Production Settings
```bash
# Database
DATABASE_USER=postgres
DATABASE_PASSWORD=your-secure-password
DATABASE_NAME=booking_system

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
CRM_BEARER_TOKEN=your-crm-token
BACKEND_SERVICE_TOKEN=your-backend-token

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Create a `.env` file in the root directory with your values.

## Health Checks

Check if everything is running:

```bash
# Backend API
curl http://localhost:5000/health

# CRM Service
curl http://localhost:5001/health

# Notification Service
curl http://localhost:5002/health

# Email Service
curl http://localhost:5003/health
```

## Troubleshooting

### "Port already in use"
```bash
# Find what's using the port
lsof -i :3000  # or :5000, :5432, etc.

# Kill the process
kill -9 <PID>
```

### "Database connection failed"
```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### "Service won't start"
```bash
# Check service logs
docker-compose logs <service-name>

# Rebuild the service
docker-compose up -d --build <service-name>
```

### "Clean slate restart"
```bash
# Stop everything and remove volumes
docker-compose down -v

# Remove all containers and images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## File Structure

```
booking-system/
├── docker-compose.yml          # Production setup
├── docker-compose.dev.yml      # Development setup
├── docker-compose.backend.yml  # Backend only
├── docker-compose.prod.yml     # Production (same as main)
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── crm_service/
│   ├── Dockerfile
│   └── app.py
├── notification_service/
│   ├── Dockerfile
│   └── app.py
├── email_service/
│   ├── Dockerfile
│   └── app.py
└── nginx/
    └── nginx.conf
```

## Development Tips

### Live Code Editing
Development mode mounts your local code into containers:
```bash
# Make changes to files locally
# Changes are reflected immediately in containers
docker-compose -f docker-compose.dev.yml up -d
```

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it booking-system-db-1 psql -U postgres -d booking_system

# View tables
\dt

# View data
SELECT * FROM users;
```

### Logs for Debugging
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 50 lines
docker-compose logs --tail=50 backend
```

