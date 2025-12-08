#!/data/data/com.termux/files/usr/bin/bash
# Check Bot Status
# Run: bash status.sh

clear
echo "╔════════════════════════════════════════════╗"
echo "║    Trading Bot Status                      ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if bot is running
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ Bot Status: RUNNING"
    echo ""
    echo "📊 Process Info:"
    ps aux | grep -E "python.*(main|server)" | grep -v grep
    echo ""
    
    # Check tmux session
    if tmux has-session -t trading 2>/dev/null; then
        echo "✅ Tmux session: ACTIVE"
        echo "   Attach: tmux attach -t trading"
    else
        echo "⚠️  Tmux session: NOT FOUND"
    fi
    
    echo ""
    echo "🔋 Wake lock status:"
    termux-wake-lock
    
else
    echo "❌ Bot Status: NOT RUNNING"
    echo ""
    echo "Start bot: bash start.sh"
fi

echo ""
echo "📋 Recent Logs (last 10 lines):"
echo "─────────────────────────────────────────────"
if ls logs/trading_*.log 1> /dev/null 2>&1; then
    tail -10 logs/trading_*.log 2>/dev/null | tail -10
else
    echo "No logs found"
fi

echo ""
echo "─────────────────────────────────────────────"
echo "Commands:"
echo "  Start:  bash start.sh"
echo "  Stop:   bash stop.sh"
echo "  Logs:   tail -f logs/trading_*.log"
