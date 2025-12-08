#!/usr/bin/env python3
"""
Bot daemon - Runs bot silently in background
Logs all output to logs/bot_output.log
"""
import subprocess
import sys
import signal
import time
from pathlib import Path

# PID file location
PID_FILE = '/tmp/trading_bot_daemon.pid'
LOG_FILE = 'logs/bot_output.log'

def is_running():
    """Check if bot is already running"""
    if not Path(PID_FILE).exists():
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        import os
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # Process doesn't exist
        Path(PID_FILE).unlink(missing_ok=True)
        return False

def start_daemon():
    """Start bot as daemon"""
    if is_running():
        print("⚠️  Bot is already running!")
        print("   Run: ./stop.sh to stop it first")
        sys.exit(1)
    
    print("🚀 Starting bot daemon...")
    
    # Create log file
    Path('logs').mkdir(exist_ok=True)
    
    # Start bot in background
    python_path = './venv/bin/python'
    
    with open(LOG_FILE, 'w') as log_f:
        process = subprocess.Popen(
            [python_path, 'main.py'],
            stdout=log_f,
            stderr=subprocess.STDOUT,
            start_new_session=True  # Detach from parent
        )
    
    # Save PID
    with open(PID_FILE, 'w') as f:
        f.write(str(process.pid))
    
    # Give it time to start
    time.sleep(2)
    
    # Verify it's running
    if is_running():
        print(f"✅ Bot started successfully!")
        print(f"   PID: {process.pid}")
        print(f"   Logs: tail -f {LOG_FILE}")
        print("")
        print("Commands:")
        print("   ./status.sh  - Check status")
        print("   ./logs.sh    - View logs")
        print("   ./stop.sh    - Stop bot")
    else:
        print("❌ Failed to start bot")
        print(f"   Check logs: cat {LOG_FILE}")
        sys.exit(1)

if __name__ == '__main__':
    start_daemon()
