#!/bin/bash
# Trendit Vercel Deployment Script
# This script prepares and deploys the Trendit API to Vercel

echo "🚀 Trendit Vercel Deployment Script"
echo "=================================="

# Ensure we're in the project root
if [[ ! -f "vercel.json" ]] || [[ ! -d "backend" ]]; then
    echo "❌ Please run this script from the Trendit project root directory"
    exit 1
fi

echo "✅ Project root confirmed: $(pwd)"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "📦 Vercel CLI version: $(vercel --version)"

# Login to Vercel (if not already logged in)
echo "🔐 Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "Please login to Vercel:"
    vercel login
else
    echo "✅ Already logged in as: $(vercel whoami)"
fi

# Set environment variables
echo "🔧 Setting up environment variables..."
echo "You need to set these environment variables in Vercel:"
echo ""
echo "Required Environment Variables:"
echo "DATABASE_URL (PostgreSQL connection string for production)"
echo "REDDIT_CLIENT_ID (from https://www.reddit.com/prefs/apps)"
echo "REDDIT_CLIENT_SECRET"
echo "REDDIT_USER_AGENT (e.g., 'Trendit/1.0 by /u/yourusername')"
echo "JWT_SECRET_KEY (generate with: openssl rand -hex 32)"
echo "API_KEY_SALT (generate with: openssl rand -hex 16)"
echo ""
echo "Optional (for billing features):"
echo "PADDLE_API_KEY"
echo "PADDLE_ENVIRONMENT (sandbox/production)"
echo "PADDLE_WEBHOOK_SECRET"
echo "PADDLE_CLIENT_TOKEN"
echo "PADDLE_PRO_PRICE_ID"
echo "PADDLE_ENTERPRISE_PRICE_ID"
echo ""
echo "Optional (for AI sentiment analysis):"
echo "OPENROUTER_API_KEY"
echo ""

read -p "Have you set all required environment variables in Vercel? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Please set environment variables first:"
    echo "1. Go to https://vercel.com/dashboard"
    echo "2. Select your project → Settings → Environment Variables"
    echo "3. Add all the variables listed above"
    echo "4. Run this script again"
    exit 1
fi

# Create a deployment-ready structure
echo "📁 Preparing deployment structure..."

# Copy requirements.txt to root for Vercel
cp backend/requirements.txt ./requirements.txt

# Create api directory structure for Vercel
mkdir -p api
cat > api/index.py << 'EOF'
from backend.main import app

# Vercel entry point
handler = app
EOF

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

# Get deployment URL
DEPLOYMENT_URL=$(vercel --prod --confirm 2>&1 | grep -o 'https://[^[:space:]]*')

if [[ -n "$DEPLOYMENT_URL" ]]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo "📍 Your API is live at: $DEPLOYMENT_URL"
    echo ""
    echo "🔗 API Endpoints:"
    echo "  Health Check: $DEPLOYMENT_URL/health"
    echo "  API Docs: $DEPLOYMENT_URL/docs"
    echo "  Authentication: $DEPLOYMENT_URL/auth/register"
    echo "  Collection Jobs: $DEPLOYMENT_URL/api/collect/jobs"
    echo ""
    echo "🧪 Test your deployment:"
    echo "  curl $DEPLOYMENT_URL/health"
    echo ""
    echo "📚 Frontend API Documentation:"
    echo "  See: TRENDIT_FRONTEND_API_SPECIFICATION.md"
    echo "  Update API_BASE_URL to: $DEPLOYMENT_URL"
else
    echo "❌ Deployment may have failed. Check Vercel dashboard for details."
    echo "🔍 Debug: vercel logs"
    exit 1
fi

# Cleanup temporary files
rm -f requirements.txt
rm -rf api/

echo "✨ Deployment complete!"