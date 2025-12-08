#!/bin/bash
# Mac - Start Trading Bot
# Run: ./start.sh

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with your API keys"
    exit 1
fi

# Use Python daemon to start bot
./venv/bin/python daemon.py
