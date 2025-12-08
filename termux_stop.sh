#!/bin/bash
# Stop Trading Bot (Works on Mac & Termux)
# Run: bash stop.sh

clear
echo "╔════════════════════════════════════════════╗"
echo "║    Stopping Crypto Trading Bot            ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if bot is running
if ! pgrep -f "python.*main.py" > /dev/null 2>&1; then
    echo "ℹ️  Bot is not running"
    exit 0
fi

echo "🛑 Stopping bot..."

# Kill tmux session if exists
if command -v tmux &> /dev/null && tmux has-session -t trading 2>/dev/null; then
    tmux kill-session -t trading
    echo "✅ Tmux session closed"
fi

# Kill any remaining python processes
pkill -f "python.*main.py" 2>/dev/null
pkill -f "python.*api/server.py" 2>/dev/null

# Disable wake lock (Termux only)
if command -v termux-wake-unlock &> /dev/null; then
    termux-wake-unlock
    echo "🔋 Wake lock disabled"
fi

# Wait and verify
sleep 1

if ! pgrep -f python > /dev/null; then
    echo ""
    echo "✅ All processes stopped successfully!"
else
    echo ""
    echo "⚠️  Some processes may still be running"
    echo "Force kill: pkill -9 python"
fi

echo ""
echo "📊 Final status:"
pgrep -af python || echo "No Python processes running"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Kill processes by PID file
if [ -f ".pids" ]; then
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping process $pid...${NC}"
            kill $pid 2>/dev/null
        fi
    done < .pids
    rm .pids
fi

# Also kill by port just to be sure
if lsof -ti :5001 > /dev/null 2>&1; then
    echo -e "${YELLOW}Stopping API server on port 5001...${NC}"
    lsof -ti :5001 | xargs kill -9 2>/dev/null
fi

if lsof -ti :3000 > /dev/null 2>&1; then
    echo -e "${YELLOW}Stopping frontend on port 3000...${NC}"
    lsof -ti :3000 | xargs kill -9 2>/dev/null
fi

echo ""
echo -e "${GREEN}✅ All services stopped!${NC}"
echo ""
