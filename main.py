#!/usr/bin/env python3
"""
Crypto Auto Trading Bot
=======================
Automated cryptocurrency trading using Binance API

Usage:
    python main.py                    # Run with default settings
    python main.py --symbol ETHUSDT   # Trade ETH/USDT
    python main.py --strategy rsi     # Use RSI strategy
    python main.py --demo             # Run demo without trading
"""

import argparse
import os
import sys

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

from bot.trading_bot import TradingBot
from exchange.binance_client import BinanceClient
from utils.logger import setup_logger
import config

logger = setup_logger('Main')

def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🚀 CRYPTO AUTO TRADING BOT 🚀                         ║
    ║                                                           ║
    ║     Powered by Binance API                                ║
    ║     Strategies: RSI, EMA Crossover, Combined              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def run_demo():
    """Run demo mode - fetch data and show signals without trading"""
    logger.info("🎮 Running in DEMO mode (no real trades)")
    
    client = BinanceClient()
    
    # Show current prices for popular pairs
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    
    print("\n📊 Current Crypto Prices:")
    print("-" * 40)
    for symbol in symbols:
        price = client.get_current_price(symbol)
        print(f"   {symbol}: ${price:,.2f}")
    print("-" * 40)
    
    # Show account balance if API keys are configured
    if config.BINANCE_API_KEY:
        print("\n💰 Account Balances:")
        balances = client.get_all_balances()
        for asset, balance in balances.items():
            if balance['total'] > 0:
                print(f"   {asset}: {balance['total']:.8f}")
    
    # Get historical data and show indicators
    print("\n📈 Technical Analysis (BTCUSDT 1H):")
    df = client.get_historical_klines('BTCUSDT', '1h', 50)
    
    if not df.empty:
        import ta
        
        # Calculate indicators
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
        df['ema_9'] = ta.trend.EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['ema_21'] = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()
        
        latest = df.iloc[-1]
        print(f"   Current Price: ${latest['close']:,.2f}")
        print(f"   RSI(14): {latest['rsi']:.2f}")
        print(f"   EMA(9): ${latest['ema_9']:,.2f}")
        print(f"   EMA(21): ${latest['ema_21']:,.2f}")
        
        # Simple signal
        if latest['rsi'] < 30:
            print("   Signal: 🟢 OVERSOLD (Potential Buy)")
        elif latest['rsi'] > 70:
            print("   Signal: 🔴 OVERBOUGHT (Potential Sell)")
        else:
            print("   Signal: ⚪ NEUTRAL")
    
    print("\n✅ Demo complete! Configure .env file to start real trading.\n")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Crypto Auto Trading Bot')
    
    parser.add_argument('--symbol', type=str, default=config.TRADE_SYMBOL,
                       help='Trading pair (e.g., BTCUSDT, ETHUSDT)')
    parser.add_argument('--quantity', type=float, default=config.TRADE_QUANTITY,
                       help='Trade quantity')
    parser.add_argument('--strategy', type=str, default='combined',
                       choices=['rsi', 'ema', 'combined'],
                       help='Trading strategy to use')
    parser.add_argument('--interval', type=int, default=60,
                       help='Check interval in seconds')
    parser.add_argument('--demo', action='store_true',
                       help='Run in demo mode (no real trades)')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check for API keys
    if not config.BINANCE_API_KEY or config.BINANCE_API_KEY == 'your_api_key_here':
        logger.warning("⚠️  Binance API key not configured!")
        logger.info("   1. Copy .env.example to .env")
        logger.info("   2. Add your Binance API keys")
        logger.info("   3. Restart the bot")
        print()
        
        if args.demo:
            # Try demo without API keys - just show public data
            run_demo()
        else:
            sys.exit(1)
        return
    
    if args.demo:
        run_demo()
        return
    
    # Create and run bot
    try:
        bot = TradingBot(
            symbol=args.symbol,
            quantity=args.quantity,
            strategy=args.strategy
        )
        
        logger.info(f"{'='*50}")
        logger.info(f"🔔 TESTNET: {config.USE_TESTNET}")
        logger.info(f"🎯 Symbol: {args.symbol}")
        logger.info(f"📊 Strategy: {args.strategy}")
        logger.info(f"⏱️  Interval: {args.interval}s")
        logger.info(f"{'='*50}")
        
        # Start the bot
        bot.run(interval_seconds=args.interval)
        
    except KeyboardInterrupt:
        logger.info("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
