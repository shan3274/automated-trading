# 📱 Termux Quick Guide

## 🚀 First Time Setup

```bash
# 1. Copy all files to Termux
# 2. Run setup script
bash termux_setup.sh

# 3. Edit .env file with your API keys
nano .env
```

## ⚡ Quick Start

```bash
# Interactive menu
bash termux_start.sh
```

## 🔧 Manual Commands

### Start Bot
```bash
termux-wake-lock  # Keep phone awake
python main.py
```

### Start API Server
```bash
python api/server.py
```

### Quick Test (5 trades)
```bash
python instant_test.py
```

### Run in Background
```bash
bash termux_background.sh
```

## 📋 Background Management

### Start background session
```bash
pkg install tmux
tmux new -s trading
python main.py
# Press Ctrl+B then D to detach
```

### Reattach to session
```bash
tmux attach -t trading
```

### Stop background bot
```bash
tmux kill-session -t trading
termux-wake-unlock
```

## 📊 Check Status

### View running processes
```bash
pgrep -af python
```

### View logs
```bash
tail -f logs/trading_$(date +%Y%m%d).log
```

### Check if bot is running
```bash
ps aux | grep python
```

## 🔋 Battery Management

### Enable wake lock (prevent sleep)
```bash
termux-wake-lock
```

### Disable wake lock
```bash
termux-wake-unlock
```

### Check wake lock status
```bash
termux-wake-lock status
```

## ⚠️ Important Notes

1. **Keep Termux running** - Don't close the app
2. **Battery optimization** - Disable for Termux in Android settings
3. **Network** - Stable WiFi recommended
4. **Storage** - Run `termux-setup-storage` for file access
5. **Wake lock** - Prevents phone from sleeping

## 🛠️ Troubleshooting

### Bot stops when screen off
```bash
# Disable battery optimization for Termux
# Settings → Apps → Termux → Battery → Unrestricted
```

### Import errors
```bash
pip install --upgrade -r requirements.txt
```

### Network timeout
```bash
# Check connection
ping google.com
# Restart bot
```

### Check logs
```bash
cat logs/trading_*.log | tail -50
```

## 📱 Recommended Setup

1. Install Termux from F-Droid (not Play Store)
2. Give storage permission
3. Disable battery optimization
4. Use WiFi (not mobile data for stability)
5. Keep phone charging while trading
6. Use tmux for background running

## 🎯 Quick Commands Cheatsheet

| Command | Description |
|---------|-------------|
| `bash termux_start.sh` | Interactive menu |
| `bash termux_background.sh` | Run bot in background |
| `python main.py` | Start trading bot |
| `python instant_test.py` | Quick test mode |
| `tmux attach -t trading` | View background bot |
| `Ctrl+B then D` | Detach from tmux |
| `tail -f logs/*.log` | Live log view |
| `pkill python` | Stop all bots |

## 📞 Support

If bot stops:
1. Check logs: `tail logs/trading_*.log`
2. Check process: `pgrep -af python`
3. Restart: `bash termux_start.sh`
