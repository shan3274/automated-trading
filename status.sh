#!/bin/bash
# Mac - Check Bot Status
# Run: ./status.sh

echo "╔════════════════════════════════════════════╗"
echo "║    Trading Bot Status                      ║"
echo "╚════════════════════════════════════════════╝"
echo ""

PID_FILE="/tmp/trading_bot_daemon.pid"

# Check if running
if [ -f "$PID_FILE" ]; then
    BOT_PID=$(cat "$PID_FILE")
    
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        echo "✅ Bot Status: RUNNING"
        echo "   PID: $BOT_PID"
        echo ""
        
        # Show open trades
        if [ -f data/trades.json ]; then
            OPEN_TRADES=$(grep -c '"status": "OPEN"' data/trades.json 2>/dev/null || echo "0")
            echo "📊 Open Trades: $OPEN_TRADES"
        fi
    else
        echo "❌ Bot Status: NOT RUNNING (stale PID)"
        rm -f "$PID_FILE"
    fi
elif pgrep -f "python.*main.py" > /dev/null 2>&1; then
    PID=$(pgrep -f "python.*main.py")
    echo "⚠️  Bot Status: RUNNING (no PID file)"
    echo "   PID: $PID"
else
    echo "❌ Bot Status: NOT RUNNING"
    echo ""
    echo "Start: ./start.sh"
fi

echo ""
echo "📋 Recent Logs (last 10 lines):"
echo "─────────────────────────────────────────────"
if [ -f logs/bot_output.log ]; then
    tail -10 logs/bot_output.log
else
    echo "No logs found"
fi
