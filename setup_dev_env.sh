#!/bin/bash
# Trendit Development Environment Setup Script
# This script standardizes the development environment setup

echo "🚀 Setting up Trendit development environment..."

# Ensure we're in the project root
if [[ ! -f "README.md" ]] || [[ ! -d "backend" ]]; then
    echo "❌ Please run this script from the Trendit project root directory"
    exit 1
fi

echo "✅ Project root confirmed: $(pwd)"

# 1. Clean up duplicate virtual environments
echo "🧹 Cleaning up duplicate virtual environments..."
if [[ -d "venv" ]]; then
    echo "   Removing root-level venv (keeping backend/venv as standard)"
    rm -rf venv
fi

if [[ ! -d "backend/venv" ]]; then
    echo "   Creating virtual environment in backend/"
    cd backend
    python -m venv venv
    cd ..
else
    echo "   ✅ Virtual environment exists at backend/venv"
fi

# 2. Standardize .env files
echo "📝 Standardizing environment configuration..."

# Remove root-level .env if it exists
if [[ -f ".env" ]]; then
    echo "   Removing root-level .env (keeping backend/.env as standard)"
    rm .env
fi

if [[ -f ".env.example" ]]; then
    echo "   Removing root-level .env.example (backend has the authoritative one)"
    rm .env.example
fi

# Ensure backend/.env exists with proper JWT secret
cd backend
if [[ ! -f ".env" ]]; then
    echo "   Creating backend/.env from example"
    cp .env.example .env
fi

# Add JWT secret if missing
if ! grep -q "JWT_SECRET_KEY=" .env; then
    echo "   Adding JWT_SECRET_KEY to .env"
    echo "" >> .env
    echo "# Generated JWT Secret (change in production)" >> .env
    echo "JWT_SECRET_KEY=trendit-dev-secret-$(openssl rand -hex 16)" >> .env
fi

cd ..

# 3. Create convenient development commands
echo "⚡ Creating development shortcuts..."

cat > run_server.sh << 'EOF'
#!/bin/bash
# Trendit Server Runner - Run from project root
cd backend
source venv/bin/activate
echo "🔥 Starting Trendit server with proper environment..."
uvicorn main:app --reload --port 8000
EOF

cat > run_tests.sh << 'EOF'
#!/bin/bash
# Trendit Test Runner - Run from project root  
cd backend
source venv/bin/activate
echo "🧪 Running Trendit test suite..."
python test_api.py
EOF

cat > install_deps.sh << 'EOF'
#!/bin/bash
# Trendit Dependency Installer - Run from project root
cd backend  
source venv/bin/activate
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt
EOF

chmod +x *.sh

# 4. Update CLAUDE.md with standardized commands
echo "📚 Updating CLAUDE.md with standardized commands..."

cat > CLAUDE_DEV_COMMANDS.md << 'EOF'
# Trendit Development Commands (Standardized)

## Directory Structure
```
Trendit/                    # Project root - run git commands here
├── backend/               # Backend code and venv
│   ├── venv/             # Virtual environment (ONLY ONE)
│   ├── .env              # Environment variables (ONLY ONE)  
│   ├── main.py           # FastAPI app
│   └── ...
├── docs/                 # Documentation
├── wiki/                 # GitHub wiki articles
├── run_server.sh         # Start development server
├── run_tests.sh          # Run test suite  
├── install_deps.sh       # Install dependencies
└── README.md
```

## Development Commands (run from project root)

### Server Management
```bash
# Start development server (auto-reload)
./run_server.sh

# Install/update dependencies  
./install_deps.sh

# Run comprehensive tests
./run_tests.sh
```

### Manual Commands (if needed)
```bash
# Activate environment manually
cd backend && source venv/bin/activate

# Run server manually
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Run tests manually  
cd backend && source venv/bin/activate && python test_api.py
```

### Git Commands (run from project root)
```bash
git status
git add .
git commit -m "Your commit message"
git push
```

## Environment Variables
- **Location**: `backend/.env` (single source of truth)
- **JWT_SECRET_KEY**: Auto-generated for development
- **Database**: PostgreSQL connection required
- **Reddit API**: Keys from https://www.reddit.com/prefs/apps
- **Paddle**: Optional for billing features

## Troubleshooting
- **"Module not found"**: Run `./install_deps.sh`  
- **"JWT_SECRET_KEY must be set"**: Run `./setup_dev_env.sh` again
- **Server won't start**: Check `backend/.env` has all required vars
- **Database errors**: Ensure PostgreSQL is running and DATABASE_URL is correct
EOF

# 5. Final verification
echo "🔍 Verifying setup..."
cd backend

# Check venv exists
if [[ ! -d "venv" ]]; then
    echo "❌ Virtual environment missing"
    exit 1
fi

# Check .env exists  
if [[ ! -f ".env" ]]; then
    echo "❌ Environment file missing"
    exit 1
fi

# Check JWT secret exists
if ! source venv/bin/activate && python -c "import os; print('JWT_SECRET_KEY:', 'SET' if os.getenv('JWT_SECRET_KEY') else 'MISSING')" 2>/dev/null; then
    echo "❌ Environment validation failed"
    exit 1
fi

cd ..

echo ""
echo "🎉 Trendit development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Start the server: ./run_server.sh"  
echo "   2. Run tests: ./run_tests.sh"
echo "   3. Check server: curl http://localhost:8000/health"
echo ""
echo "📚 See CLAUDE_DEV_COMMANDS.md for all commands"
EOF