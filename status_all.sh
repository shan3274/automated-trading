#!/bin/bash
# Check Status of All Services
# Run: ./status_all.sh

echo "╔═══════════════════════════════════════════╗"
echo "║     Trading System Status                 ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# 1. Trading Bot Status
echo "1️⃣  Trading Bot:"
PID_FILE="/tmp/trading_bot_daemon.pid"
if [ -f "$PID_FILE" ]; then
    BOT_PID=$(cat "$PID_FILE")
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        echo "   ✅ Running (PID: $BOT_PID)"
    else
        echo "   ❌ Not Running"
    fi
else
    echo "   ❌ Not Running"
fi
echo ""

# 2. API Server Status
echo "2️⃣  API Server (port 5001):"
if lsof -i:5001 > /dev/null 2>&1; then
    API_PID=$(lsof -ti:5001)
    echo "   ✅ Running (PID: $API_PID)"
else
    echo "   ❌ Not Running"
fi
echo ""

# 3. Frontend Status
echo "3️⃣  Frontend (port 3000):"
if lsof -i:3000 > /dev/null 2>&1; then
    FRONTEND_PID=$(lsof -ti:3000)
    echo "   ✅ Running (PID: $FRONTEND_PID)"
else
    echo "   ❌ Not Running"
fi
echo ""

# Show URLs if running
if lsof -i:3000 > /dev/null 2>&1; then
    echo "🌐 Access URLs:"
    echo "   Dashboard: http://localhost:3000"
    echo "   API:       http://localhost:5001"
    echo ""
fi

# Show open trades
if [ -f data/trades.json ]; then
    OPEN_TRADES=$(grep -c '"status": "OPEN"' data/trades.json 2>/dev/null || echo "0")
    echo "📊 Open Trades: $OPEN_TRADES"
    echo ""
fi

echo "Commands:"
echo "  ./start_all.sh  - Start all services"
echo "  ./stop_all.sh   - Stop all services"
echo "  ./logs.sh       - View bot logs"
