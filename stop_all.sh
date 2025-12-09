#!/bin/bash
# Stop Everything - Bot + API + Frontend
# Run: ./stop_all.sh

echo "🛑 Stopping All Services..."
echo ""

# 1. Stop Trading Bot (with trade closing)
echo "1️⃣  Stopping Trading Bot & Closing Open Trades..."
./stop.sh
echo ""

# 2. Stop API Server
echo "2️⃣  Stopping API Server..."
# First try PID file
if [ -f /tmp/api_server.pid ]; then
    API_PID=$(cat /tmp/api_server.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        kill $API_PID 2>/dev/null
        sleep 1
        # Force kill if still running
        if ps -p $API_PID > /dev/null 2>&1; then
            kill -9 $API_PID 2>/dev/null
        fi
        echo "   ✅ API Server stopped (PID: $API_PID)"
    fi
    rm -f /tmp/api_server.pid
fi

# Kill all python server.py processes
if pgrep -f "python.*server.py" > /dev/null 2>&1; then
    pkill -9 -f "python.*server.py"
    echo "   ✅ All API Server processes stopped"
else
    echo "   ℹ️  API Server not running"
fi
echo ""

# 3. Stop Frontend
echo "3️⃣  Stopping Frontend..."
# First try PID file
if [ -f /tmp/frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        sleep 1
        # Force kill if still running
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill -9 $FRONTEND_PID 2>/dev/null
        fi
        echo "   ✅ Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f /tmp/frontend.pid
fi

# Kill all processes on port 3000
if lsof -ti:3000 > /dev/null 2>&1; then
    kill -9 $(lsof -ti:3000) 2>/dev/null
    echo "   ✅ Frontend (port 3000) stopped"
else
    echo "   ℹ️  Frontend not running"
fi

# Kill all npm/react-scripts processes
if pgrep -f "react-scripts" > /dev/null 2>&1; then
    pkill -9 -f "react-scripts"
    echo "   ✅ All React processes stopped"
fi

if pgrep -f "npm start" > /dev/null 2>&1; then
    pkill -9 -f "npm start"
    echo "   ✅ All npm processes stopped"
fi
echo ""

echo "✅ All services stopped!"
