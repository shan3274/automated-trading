# 🚀 Crypto Auto Trading Bot

Automated cryptocurrency trading bot using Binance API with multiple trading strategies.

## Features

- 📊 **Multiple Strategies**: RSI, EMA Crossover, and Combined Strategy
- 🔄 **Auto Trading**: Fully automated buy/sell execution
- 🛡️ **Risk Management**: Stop-loss and take-profit features
- 🧪 **Testnet Support**: Practice trading without real money
- 📈 **Real-time Data**: Live price updates and technical indicators
- 📝 **Logging**: Detailed logs for all activities

## Installation

### 1. Clone and Setup

```bash
cd /Users/shan/Desktop/Automate-trading
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Binance API keys
```

**Get API Keys:**
1. Go to [Binance](https://www.binance.com)
2. Navigate to API Management
3. Create a new API key
4. Enable Spot & Margin Trading
5. (Optional) Restrict to your IP for security

**For Testnet (Recommended for testing):**
1. Go to [Binance Testnet](https://testnet.binance.vision/)
2. Login with GitHub
3. Generate API keys
4. Set `USE_TESTNET=True` in `.env`

## Usage

### Demo Mode (No Trading)
```bash
python main.py --demo
```

### Start Trading
```bash
# Default settings (BTCUSDT, Combined Strategy)
python main.py

# Custom settings
python main.py --symbol ETHUSDT --strategy rsi --interval 120

# Options:
#   --symbol    : Trading pair (BTCUSDT, ETHUSDT, etc.)
#   --quantity  : Amount to trade
#   --strategy  : rsi, ema, or combined
#   --interval  : Check interval in seconds
```

## Trading Strategies

### 1. RSI Strategy
- **Buy**: When RSI < 30 (oversold)
- **Sell**: When RSI > 70 (overbought)

### 2. EMA Crossover Strategy
- **Buy**: When EMA(9) crosses above EMA(21) - Golden Cross
- **Sell**: When EMA(9) crosses below EMA(21) - Death Cross

### 3. Combined Strategy (Recommended)
Uses multiple indicators for confirmation:
- RSI for overbought/oversold
- EMA crossovers for trend
- MACD for momentum
- Bollinger Bands for volatility

## Configuration

Edit `config.py` to customize:

```python
# Trading Settings
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.001

# Strategy Parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

EMA_SHORT_PERIOD = 9
EMA_LONG_PERIOD = 21

# Risk Management
STOP_LOSS_PERCENT = 2.0
TAKE_PROFIT_PERCENT = 4.0
```

## Project Structure

```
Automate-trading/
├── main.py                    # Entry point
├── config.py                  # Configuration settings
├── requirements.txt           # Dependencies
├── .env                       # API keys (create from .env.example)
├── bot/
│   └── trading_bot.py         # Main bot logic
├── exchange/
│   └── binance_client.py      # Binance API wrapper
├── strategies/
│   ├── base_strategy.py       # Base strategy class
│   ├── rsi_strategy.py        # RSI strategy
│   ├── ema_crossover_strategy.py  # EMA strategy
│   └── combined_strategy.py   # Combined strategy
├── utils/
│   └── logger.py              # Logging utilities
└── logs/                      # Log files
```

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK!**

- This bot is for educational purposes
- Cryptocurrency trading involves significant risk
- Never trade with money you can't afford to lose
- Always test on Testnet first
- Past performance doesn't guarantee future results

## Tips for Safe Trading

1. **Start with Testnet** - Practice without real money
2. **Small Amounts** - Start with small quantities
3. **Stop-Loss** - Always use stop-loss orders
4. **Monitor** - Don't leave the bot unattended for long periods
5. **Understand** - Make sure you understand the strategies before using

## License

MIT License - Feel free to modify and use!

---
Made with ❤️ for crypto traders
