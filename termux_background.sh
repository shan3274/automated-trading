#!/data/data/com.termux/files/usr/bin/bash
# Background Bot Runner for Termux
# Runs bot in background with tmux

echo "🚀 Starting bot in background..."

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "📦 Installing tmux..."
    pkg install -y tmux
fi

# Check if session exists
if tmux has-session -t trading 2>/dev/null; then
    echo "⚠️  Trading session already exists!"
    echo ""
    echo "Options:"
    echo "1) Attach to existing: tmux attach -t trading"
    echo "2) Kill and restart: tmux kill-session -t trading && bash $0"
    exit 1
fi

# Start new tmux session with bot
echo "🎯 Creating new trading session..."
termux-wake-lock

# Create session and run bot
tmux new-session -d -s trading "python main.py"

echo ""
echo "✅ Bot started in background!"
echo ""
echo "📱 Commands:"
echo "   View bot:    tmux attach -t trading"
echo "   Detach:      Press Ctrl+B then D"
echo "   Stop bot:    tmux kill-session -t trading"
echo "   Check logs:  tail -f logs/trading_*.log"
echo ""
echo "🔋 Wake lock enabled - bot will keep running"
echo "💡 To stop wake lock: termux-wake-unlock"
