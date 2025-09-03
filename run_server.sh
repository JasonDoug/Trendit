#!/bin/bash
# Trendit Server Runner - Run from project root
cd backend
source venv/bin/activate
echo "🔥 Starting Trendit server with proper environment..."
uvicorn main:app --reload --port 8000
