"""
Configuration settings for the Crypto Trading Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Binance API Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Use testnet for paper trading (recommended for testing)
USE_TESTNET = os.getenv('USE_TESTNET', 'True').lower() == 'true'

# Testnet URLs
TESTNET_API_URL = 'https://testnet.binance.vision/api'
TESTNET_WS_URL = 'wss://testnet.binance.vision/ws'

# Trading Configuration
TRADE_SYMBOL = os.getenv('TRADE_SYMBOL', 'BTCUSDT')
TRADE_QUANTITY = float(os.getenv('TRADE_QUANTITY', '0.001'))

# Strategy Settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

EMA_SHORT_PERIOD = 9
EMA_LONG_PERIOD = 21

# Risk Management
STOP_LOSS_PERCENT = 2.0  # 2% stop loss
TAKE_PROFIT_PERCENT = 4.0  # 4% take profit
MAX_POSITION_SIZE = 0.1  # Maximum 10% of portfolio per trade

# Logging
LOG_LEVEL = 'INFO'
