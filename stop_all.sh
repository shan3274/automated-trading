#!/bin/bash
# Stop Everything - Bot + API + Frontend
# Run: ./stop_all.sh

echo "🛑 Stopping All Services..."
echo ""

# 1. Stop Trading Bot
echo "1️⃣  Stopping Trading Bot..."
./stop.sh
echo ""

# 2. Stop API Server
echo "2️⃣  Stopping API Server..."
if [ -f /tmp/api_server.pid ]; then
    API_PID=$(cat /tmp/api_server.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        kill $API_PID 2>/dev/null
        echo "   ✅ API Server stopped (PID: $API_PID)"
    else
        echo "   ℹ️  API Server not running"
    fi
    rm -f /tmp/api_server.pid
else
    # Fallback - kill any python server.py
    if pgrep -f "python.*server.py" > /dev/null 2>&1; then
        pkill -f "python.*server.py"
        echo "   ✅ API Server stopped"
    else
        echo "   ℹ️  API Server not running"
    fi
fi
echo ""

# 3. Stop Frontend
echo "3️⃣  Stopping Frontend..."
if [ -f /tmp/frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   ✅ Frontend stopped (PID: $FRONTEND_PID)"
    else
        echo "   ℹ️  Frontend not running"
    fi
    rm -f /tmp/frontend.pid
else
    # Fallback - kill any npm/node on port 3000
    if lsof -ti:3000 > /dev/null 2>&1; then
        kill -9 $(lsof -ti:3000) 2>/dev/null
        echo "   ✅ Frontend stopped"
    else
        echo "   ℹ️  Frontend not running"
    fi
fi
echo ""

echo "✅ All services stopped!"
