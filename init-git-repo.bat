#!/bin/bash

# Git initialization and structured commits script
# This script initializes a git repository and creates structured commits for the booking system

echo "🚀 Initializing Git repository and creating structured commits..."
echo "=================================================="

# Initialize git repository
echo "📁 Initializing Git repository..."
git init

# Create .gitignore file
echo "📝 Creating .gitignore file..."
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Database
*.db
*.sqlite
*.sqlite3
instance/

# Docker
.dockerignore

# Build outputs
build/
dist/
*.tgz
*.tar.gz

# Coverage
coverage/
*.lcov

# Temporary files
*.tmp
*.temp
.cache/

# Lock files (keep package-lock.json but ignore others)
pnpm-lock.yaml
yarn.lock

# Test files
test_websocket.py
test_websocket_enhanced.py

# Documentation that might be outdated
DOCKER_README.md
IMPLEMENTATION_SUMMARY.md
EOF

echo "✅ .gitignore created"

# Stage .gitignore first
git add .gitignore
git commit -m "chore: add .gitignore for Python, Node.js, Docker, and IDEs"

echo "📦 Commit 1: .gitignore file created"

# Commit 1: Backend core infrastructure
echo "🔧 Creating commit 1: Backend core infrastructure..."
git add backend/
git commit -m "feat: add Flask backend with SQLAlchemy models and JWT auth"

echo "📦 Commit 1: Backend core infrastructure completed"

# Commit 2: CRM service
echo "🏢 Creating commit 2: CRM service..."
git add crm_service/
git commit -m "feat: add CRM microservice for customer management"

echo "📦 Commit 2: CRM service completed"

# Commit 3: Notification service
echo "🔔 Creating commit 3: Notification service..."
git add notification_service/
git commit -m "feat: add WebSocket notification service with Flask-SocketIO"

echo "📦 Commit 3: Notification service completed"

# Commit 4: Authentication and session management
echo "🔐 Creating commit 4: Authentication and session management..."
git add backend/app.py -p || git add backend/app.py
git commit -m "feat: add auth endpoints and session management API"

echo "📦 Commit 4: Authentication and session management completed"

# Commit 5: Booking system
echo "📅 Creating commit 5: Booking system..."
git add backend/app.py -p || git add backend/app.py
git commit -m "feat: add booking API with capacity validation and notifications"

echo "📦 Commit 5: Booking system completed"

# Commit 6: Facilitator dashboard API
echo "📊 Creating commit 6: Facilitator dashboard API..."
git add backend/app.py -p || git add backend/app.py
git commit -m "feat: add facilitator dashboard API with metrics and analytics"

echo "📦 Commit 6: Facilitator dashboard API completed"

# Commit 7: Docker configuration
echo "🐳 Creating commit 7: Docker configuration..."
git add docker-compose.backend.yml Dockerfile */Dockerfile */.dockerignore start-backend.bat
git commit -m "feat: add Docker containerization for all services"

echo "📦 Commit 7: Docker configuration completed"

# Commit 8: Frontend core infrastructure
echo "⚛️ Creating commit 8: Frontend core infrastructure..."
git add frontend/src/contexts/ frontend/src/components/ProtectedRoute.tsx frontend/src/components/Navbar.tsx frontend/package.json frontend/tailwind.config.js
git commit -m "feat: add React frontend with auth context and protected routes"

echo "📦 Commit 8: Frontend core infrastructure completed"

# Commit 9: User authentication pages
echo "🔑 Creating commit 9: User authentication pages..."
git add frontend/src/pages/Login.tsx frontend/src/pages/Register.tsx frontend/src/pages/Home.tsx
git commit -m "feat: add login, register, and home pages with form validation"

echo "📦 Commit 9: User authentication pages completed"

# Commit 10: User dashboard
echo "📊 Creating commit 10: User dashboard..."
git add frontend/src/pages/Dashboard.tsx frontend/src/pages/Bookings.tsx frontend/src/pages/Sessions.tsx
git commit -m "feat: add user dashboard with booking and session management"

echo "📦 Commit 10: User dashboard completed"

# Commit 11: Facilitator dashboard
echo "👨‍🏫 Creating commit 11: Facilitator dashboard..."
git add frontend/src/pages/FacilitatorDashboard.tsx frontend/src/pages/CreateSession.tsx
git commit -m "feat: add facilitator dashboard with metrics and session management"

echo "📦 Commit 11: Facilitator dashboard completed"

# Commit 12: Frontend routing and integration
echo "🔗 Creating commit 12: Frontend routing and integration..."
git add frontend/src/App.tsx frontend/src/components/
git commit -m "feat: add React Router with role-based routing and navigation"

echo "📦 Commit 12: Frontend routing and integration completed"

# Commit 13: Configuration and utilities
echo "⚙️ Creating commit 13: Configuration and utilities..."
git add config_manager.py components.json 
git commit -m "feat: add Shadcn UI components and styling system"

echo "📦 Commit 13: Configuration and utilities completed"

# Commit 14: Documentation and project structure
echo "📚 Creating commit 14: Documentation and project structure..."
git add README.md start-backend.bat
git commit -m "docs: add README and setup scripts"

echo "📦 Commit 14: Documentation and project structure completed"



✅ Multi-service architecture with Docker
✅ JWT authentication and role-based access
✅ Real-time notifications via WebSocket
✅ User and facilitator dashboards
✅ Session and booking management
✅ Revenue tracking and analytics
✅ Responsive React frontend with TypeScript"

# Create version tag
echo "🏷️ Creating version tag v1.0.0..."
git tag -a v1.0.0 -m "v1.0.0 - Complete booking system with user/facilitator dashboards"

echo ""
echo "🎉 Git repository initialized with structured commits!"
echo "📊 Summary:"
echo "   - 14 structured commits created"
echo "   - Version tagged as v1.0.0"
echo "   - Complete project history preserved"
echo ""
echo "📋 Next steps:"
echo "   1. Review commit history: git log --oneline"
echo "   2. Push to remote: git remote add origin <url> && git push -u origin main"
echo "   3. Create release: git push --tags"
echo ""
echo "✨ Repository ready for development and deployment!"
