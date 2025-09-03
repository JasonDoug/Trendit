#!/bin/bash
# Trendit Test Runner - Run from project root  
cd backend
source venv/bin/activate
echo "🧪 Running Trendit test suite..."
python test_api.py
