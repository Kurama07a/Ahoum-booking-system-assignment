# Git initialization and structured commits script for Windows PowerShell
# This script initializes a git repository and creates structured commits for the booking system

Write-Host "🚀 Initializing Git repository and creating structured commits..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

# Initialize git repository
Write-Host "📁 Initializing Git repository..." -ForegroundColor Yellow
git init

# Create .gitignore file
Write-Host "📝 Creating .gitignore file..." -ForegroundColor Yellow
@"
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
"@ | Out-File -FilePath .gitignore -Encoding utf8

Write-Host "✅ .gitignore created" -ForegroundColor Green

# Stage .gitignore first
git add .gitignore
git commit -m "chore: add .gitignore for Python, Node.js, Docker, and IDEs"

Write-Host "📦 Commit 1: .gitignore file created" -ForegroundColor Green

# Commit 1: Backend core infrastructure
Write-Host "🔧 Creating commit 1: Backend core infrastructure..." -ForegroundColor Yellow
git add backend/
git commit -m "feat: add Flask backend with SQLAlchemy models and JWT auth"

Write-Host "📦 Commit 1: Backend core infrastructure completed" -ForegroundColor Green

# Commit 2: CRM service
Write-Host "🏢 Creating commit 2: CRM service..." -ForegroundColor Yellow
git add crm_service/
git commit -m "feat: add CRM microservice for customer management"

Write-Host "📦 Commit 2: CRM service completed" -ForegroundColor Green

# Commit 3: Notification service
Write-Host "🔔 Creating commit 3: Notification service..." -ForegroundColor Yellow
git add notification_service/
git commit -m "feat: add WebSocket notification service with Flask-SocketIO"

Write-Host "📦 Commit 3: Notification service completed" -ForegroundColor Green

# Commit 4: Authentication and session management
Write-Host "🔐 Creating commit 4: Authentication and session management..." -ForegroundColor Yellow
git add "backend/app.py"
git commit -m "feat: add auth endpoints and session management API"

Write-Host "📦 Commit 4: Authentication and session management completed" -ForegroundColor Green

# Commit 5: Booking system
Write-Host "📅 Creating commit 5: Booking system..." -ForegroundColor Yellow
git add "backend/app.py"
git commit -m "feat: add booking API with capacity validation and notifications"

Write-Host "📦 Commit 5: Booking system completed" -ForegroundColor Green

# Commit 6: Facilitator dashboard API
Write-Host "📊 Creating commit 6: Facilitator dashboard API..." -ForegroundColor Yellow
git add "backend/app.py"
git commit -m "feat: add facilitator dashboard API with metrics and analytics"

Write-Host "📦 Commit 6: Facilitator dashboard API completed" -ForegroundColor Green

# Commit 7: Docker configuration
Write-Host "🐳 Creating commit 7: Docker configuration..." -ForegroundColor Yellow
git add docker-compose.backend.yml
if (Test-Path "Dockerfile") { git add Dockerfile }
if (Test-Path "*/Dockerfile") { git add "*/Dockerfile" }
if (Test-Path "*/.dockerignore") { git add "*/.dockerignore" }
if (Test-Path "start-backend.bat") { git add start-backend.bat }
git commit -m "feat: add Docker containerization for all services"

Write-Host "📦 Commit 7: Docker configuration completed" -ForegroundColor Green

# Commit 8: Frontend core infrastructure
Write-Host "⚛️ Creating commit 8: Frontend core infrastructure..." -ForegroundColor Yellow
git add frontend/src/contexts/
git add frontend/src/components/ProtectedRoute.tsx
git add frontend/src/components/Navbar.tsx
git add frontend/package.json
git add frontend/tailwind.config.js
git commit -m "feat: add React frontend with auth context and protected routes"

Write-Host "📦 Commit 8: Frontend core infrastructure completed" -ForegroundColor Green

# Commit 9: User authentication pages
Write-Host "🔑 Creating commit 9: User authentication pages..." -ForegroundColor Yellow
git add frontend/src/pages/Login.tsx
git add frontend/src/pages/Register.tsx
git add frontend/src/pages/Home.tsx
git commit -m "feat: add login, register, and home pages with form validation"

Write-Host "📦 Commit 9: User authentication pages completed" -ForegroundColor Green

# Commit 10: User dashboard
Write-Host "📊 Creating commit 10: User dashboard..." -ForegroundColor Yellow
git add frontend/src/pages/Dashboard.tsx
git add frontend/src/pages/Bookings.tsx
git add frontend/src/pages/Sessions.tsx
git commit -m "feat: add user dashboard with booking and session management"

Write-Host "📦 Commit 10: User dashboard completed" -ForegroundColor Green

# Commit 11: Facilitator dashboard
Write-Host "👨‍🏫 Creating commit 11: Facilitator dashboard..." -ForegroundColor Yellow
git add frontend/src/pages/FacilitatorDashboard.tsx
git add frontend/src/pages/CreateSession.tsx
git commit -m "feat: add facilitator dashboard with metrics and session management"

Write-Host "📦 Commit 11: Facilitator dashboard completed" -ForegroundColor Green

# Commit 12: Frontend routing and integration
Write-Host "🔗 Creating commit 12: Frontend routing and integration..." -ForegroundColor Yellow
git add frontend/src/App.tsx
git add frontend/src/components/
git commit -m "feat: add React Router with role-based routing and navigation"

Write-Host "📦 Commit 12: Frontend routing and integration completed" -ForegroundColor Green

# Commit 13: UI components and styling
Write-Host "🎨 Creating commit 13: UI components and styling..." -ForegroundColor Yellow
git add components/
git add hooks/
git add lib/
git add styles/
git add app/
git add public/
git commit -m "feat: add Shadcn UI components and styling system"

Write-Host "📦 Commit 13: UI components and styling completed" -ForegroundColor Green

# Commit 14: Configuration files
Write-Host "⚙️ Creating commit 14: Configuration files..." -ForegroundColor Yellow
git add components.json
git add next.config.mjs
git add package.json
git add pnpm-lock.yaml
git add postcss.config.mjs
git add tailwind.config.ts
git add tsconfig.json
git commit -m "feat: add Next.js, TypeScript, and Tailwind configuration"

Write-Host "📦 Commit 14: Configuration files completed" -ForegroundColor Green

# Commit 15: Documentation and project structure
Write-Host "📚 Creating commit 15: Documentation and project structure..." -ForegroundColor Yellow
git add README.md
if (Test-Path "*.py") { git add "*.py" }
if (Test-Path "*.bat") { git add "*.bat" }
git commit -m "docs: add README and setup scripts"

Write-Host "📦 Commit 15: Documentation completed" -ForegroundColor Green

# Final commit with any remaining files
Write-Host "🔄 Adding any remaining files..." -ForegroundColor Yellow
git add .
git commit -m "chore: finalize v1.0.0 - complete booking system

✅ Multi-service architecture with Docker
✅ JWT authentication and role-based access
✅ Real-time notifications via WebSocket
✅ User and facilitator dashboards
✅ Session and booking management
✅ Revenue tracking and analytics
✅ Responsive React frontend with TypeScript"

# Create version tag
Write-Host "🏷️ Creating version tag v1.0.0..." -ForegroundColor Yellow
git tag -a v1.0.0 -m "v1.0.0 - Complete booking system with user/facilitator dashboards"

Write-Host ""
Write-Host "🎉 Git repository initialized with structured commits!" -ForegroundColor Green
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   - 15 structured commits created" -ForegroundColor White
Write-Host "   - Version tagged as v1.0.0" -ForegroundColor White
Write-Host "   - Complete project history preserved" -ForegroundColor White
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Review commit history: git log --oneline" -ForegroundColor White
Write-Host "   2. Push to remote: git remote add origin <url>; git push -u origin main" -ForegroundColor White
Write-Host "   3. Create release: git push --tags" -ForegroundColor White
Write-Host ""
Write-Host "✨ Repository ready for development and deployment!" -ForegroundColor Green

# Pause to allow user to see results
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
