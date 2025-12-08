#!/usr/bin/env python3
"""
Bot runner - Keeps bot running in a subprocess
"""
import subprocess
import sys
import signal
import time

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n👋 Stopping bot...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    # Get Python path from venv
    python_path = './venv/bin/python'
    
    print("🚀 Starting bot in background...")
    print("   Press Ctrl+C to stop")
    print("")
    
    # Run bot as subprocess
    try:
        process = subprocess.Popen(
            [python_path, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
        
    except KeyboardInterrupt:
        print('\n👋 Bot stopped by user')
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
