#!/bin/bash
# Trendit Dependency Installer - Run from project root
cd backend  
source venv/bin/activate
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt
