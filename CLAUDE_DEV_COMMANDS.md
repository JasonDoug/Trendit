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
