#!/data/data/com.termux/files/usr/bin/bash
# Start Trading Bot in Background
# Run: bash start.sh

clear
echo "╔════════════════════════════════════════════╗"
echo "║    Starting Crypto Trading Bot            ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "Please run setup first:"
    echo "   bash termux_setup.sh"
    echo ""
    exit 1
fi

# Check if already running
if pgrep -f "python.*main.py" > /dev/null; then
    echo "⚠️  Bot is already running!"
    echo ""
    echo "Check status: bash status.sh"
    echo "Stop bot: bash stop.sh"
    exit 1
fi

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "📦 Installing tmux..."
    pkg install -y tmux
fi

# Enable wake lock
echo "🔋 Enabling wake lock..."
termux-wake-lock

# Start bot in tmux
echo "🚀 Starting bot in background..."
tmux new-session -d -s trading "python main.py"

# Wait a bit and check
sleep 2

if pgrep -f "python.*main.py" > /dev/null; then
    echo ""
    echo "✅ Bot started successfully!"
    echo ""
    echo "📱 Commands:"
    echo "   View bot:    tmux attach -t trading"
    echo "   Detach:      Ctrl+B then D"
    echo "   View logs:   tail -f logs/trading_*.log"
    echo "   Stop bot:    bash stop.sh"
    echo ""
    echo "🔋 Wake lock enabled - bot will keep running"
else
    echo ""
    echo "❌ Failed to start bot!"
    echo "Check logs: cat logs/trading_*.log"
fi
