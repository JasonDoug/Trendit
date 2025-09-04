#!/bin/bash
# Trendit Server Stopper - Stop all running uvicorn instances
echo "🛑 Stopping Trendit server..."

# Find processes using port 8000
port_pids=$(lsof -t -i :8000 2>/dev/null | grep -v "^$" || true)

# Find uvicorn processes by command line
uvicorn_pids=$(pgrep -f "uvicorn main:app" || true)
python_uvicorn_pids=$(pgrep -f "python.*uvicorn.*main:app" || true)

# Combine all PIDs
all_pids=$(echo "$port_pids $uvicorn_pids $python_uvicorn_pids" | tr ' ' '\n' | sort -u | grep -v "^$" || true)

if [ -z "$all_pids" ]; then
    echo "No running Trendit server found."
else
    echo "Found running server processes: $all_pids"
    for pid in $all_pids; do
        echo "Killing process $pid"
        kill $pid 2>/dev/null || true
    done
    sleep 1
    
    # Force kill if still running
    remaining=$(lsof -t -i :8000 2>/dev/null || true)
    if [ ! -z "$remaining" ]; then
        echo "Force killing remaining processes on port 8000: $remaining"
        kill -9 $remaining 2>/dev/null || true
    fi
    
    echo "✅ Trendit server stopped."
fi