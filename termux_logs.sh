#!/bin/bash
# View Live Logs (Works on Mac & Termux)
# Run: bash logs.sh

clear
echo "╔════════════════════════════════════════════╗"
echo "║    Trading Bot - Live Logs                 ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to exit"
echo ""

# Find latest log file
LOG_FILE=$(ls -t logs/trading_*.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "❌ No log files found"
    exit 1
fi

echo "📋 Watching: $LOG_FILE"
echo "─────────────────────────────────────────────"
echo ""

# Follow log file
tail -f "$LOG_FILE"
