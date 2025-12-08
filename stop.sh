#!/bin/bash
# Mac - Stop Trading Bot
# Run: ./stop.sh

echo "🛑 Stopping Crypto Trading Bot..."
echo ""

PID_FILE="/tmp/trading_bot_daemon.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    # Try to kill any running python main.py process
    if pgrep -f "python.*main.py" > /dev/null 2>&1; then
        pkill -f "python.*main.py"
        echo "✅ Bot stopped"
    else
        echo "ℹ️  Bot is not running"
    fi
    exit 0
fi

# Get PID
BOT_PID=$(cat "$PID_FILE")

# Kill process
if ps -p "$BOT_PID" > /dev/null 2>&1; then
    kill "$BOT_PID"
    sleep 1
    
    # Force kill if still running
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        kill -9 "$BOT_PID"
    fi
    
    echo "✅ Bot stopped (PID: $BOT_PID)"
else
    echo "ℹ️  Bot process not found"
fi

# Remove PID file
rm -f "$PID_FILE"
