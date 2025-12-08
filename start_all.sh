#!/bin/bash
# Start Everything - Bot + API + Frontend
# Run: ./start_all.sh

echo "🚀 Starting Complete Trading System..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with your API keys"
    exit 1
fi

# 1. Start Trading Bot
echo "1️⃣  Starting Trading Bot..."
./start.sh
sleep 2
echo ""

# 2. Start API Server
echo "2️⃣  Starting API Server (port 5001)..."
nohup ./venv/bin/python api/server.py > logs/api_server.log 2>&1 &
API_PID=$!
echo $API_PID > /tmp/api_server.pid
sleep 2

# Check if API started successfully
if ps -p $API_PID > /dev/null 2>&1; then
    echo "   ✅ API Server started (PID: $API_PID)"
else
    echo "   ❌ API Server failed to start"
    echo "   Check: cat logs/api_server.log"
fi
echo ""

# 3. Start Frontend
echo "3️⃣  Starting Frontend (port 3000)..."
cd frontend
nohup npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/frontend.pid
cd ..
sleep 3
echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

echo "╔═══════════════════════════════════════════╗"
echo "║  ✅ All Services Started Successfully!    ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "📊 Dashboard:  http://localhost:3000"
echo "🔌 API:        http://localhost:5001"
echo ""
echo "Commands:"
echo "  ./status_all.sh  - Check all services"
echo "  ./stop_all.sh    - Stop all services"
echo "  ./logs.sh        - View bot logs"
echo ""
