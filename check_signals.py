"""Quick script to check current market conditions and signals"""
import sys
from exchange.binance_client import BinanceClient
from strategies.combined_strategy import CombinedStrategy
import config

def main():
    print("🔍 Checking current market conditions...\n")
    
    # Initialize client and strategy
    client = BinanceClient()
    strategy = CombinedStrategy()
    
    # Get current price
    symbol = config.TRADE_SYMBOL
    current_price = client.get_current_price(symbol)
    print(f"💵 Current {symbol} Price: ${current_price:,.2f}\n")
    
    # Get historical data
    df = client.get_historical_klines(symbol, interval='1h', limit=100)
    
    if df.empty:
        print("❌ No data available!")
        return
    
    # Calculate indicators
    df = strategy.calculate_indicators(df)
    
    # Show last values
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    print("📊 Technical Indicators:")
    print(f"   RSI (14):           {last['rsi']:.2f}")
    print(f"   EMA Short (9):      ${last['ema_short']:.2f}")
    print(f"   EMA Long (21):      ${last['ema_long']:.2f}")
    print(f"   MACD Histogram:     {last['macd_histogram']:.4f}")
    print(f"   Bollinger Upper:    ${last['bb_upper']:.2f}")
    print(f"   Bollinger Lower:    ${last['bb_lower']:.2f}")
    print()
    
    # Check conditions
    print("🎯 Signal Analysis:")
    
    bullish = 0
    bearish = 0
    
    # RSI
    if last['rsi'] < config.RSI_OVERSOLD:
        print(f"   ✅ RSI Oversold ({last['rsi']:.2f} < {config.RSI_OVERSOLD}) → BULLISH")
        bullish += 1
    elif last['rsi'] > config.RSI_OVERBOUGHT:
        print(f"   ❌ RSI Overbought ({last['rsi']:.2f} > {config.RSI_OVERBOUGHT}) → BEARISH")
        bearish += 1
    else:
        print(f"   ⏸️  RSI Neutral ({last['rsi']:.2f})")
    
    # EMA Crossover
    if prev['ema_short'] <= prev['ema_long'] and last['ema_short'] > last['ema_long']:
        print(f"   ✅ EMA Bullish Crossover → BULLISH")
        bullish += 1
    elif prev['ema_short'] >= prev['ema_long'] and last['ema_short'] < last['ema_long']:
        print(f"   ❌ EMA Bearish Crossover → BEARISH")
        bearish += 1
    else:
        if last['ema_short'] > last['ema_long']:
            print(f"   📈 EMA Trend: Bullish (no crossover)")
            bullish += 0.5
        else:
            print(f"   📉 EMA Trend: Bearish (no crossover)")
            bearish += 0.5
    
    # MACD
    if prev['macd_histogram'] < 0 and last['macd_histogram'] > 0:
        print(f"   ✅ MACD Bullish Cross → BULLISH")
        bullish += 1
    elif prev['macd_histogram'] > 0 and last['macd_histogram'] < 0:
        print(f"   ❌ MACD Bearish Cross → BEARISH")
        bearish += 1
    else:
        print(f"   ⏸️  MACD: {last['macd_histogram']:.4f} (no cross)")
    
    # Bollinger Bands
    if current_price < last['bb_lower']:
        print(f"   ✅ Price below BB Lower (${current_price:.2f} < ${last['bb_lower']:.2f}) → BULLISH")
        bullish += 0.5
    elif current_price > last['bb_upper']:
        print(f"   ❌ Price above BB Upper (${current_price:.2f} > ${last['bb_upper']:.2f}) → BEARISH")
        bearish += 0.5
    else:
        print(f"   ⏸️  Price within Bollinger Bands")
    
    print()
    print(f"📊 Total Signals: Bullish = {bullish}, Bearish = {bearish}")
    print()
    
    # Generate signal
    signal = strategy.generate_signal(df)
    
    if signal.name == 'BUY':
        print("🟢 SIGNAL: **BUY** - Trade will execute!")
    elif signal.name == 'SELL':
        print("🔴 SIGNAL: **SELL** - Trade will execute!")
    else:
        print("⏸️  SIGNAL: **HOLD** - Waiting for better conditions...")
        print()
        print("💡 Why no trade?")
        print(f"   - Need at least 2.0 bullish signals for BUY")
        print(f"   - Need at least 2.0 bearish signals for SELL")
        print(f"   - Current bullish: {bullish}")
        print(f"   - Current bearish: {bearish}")
        print()
        print("🔧 Market is likely in a sideways/ranging phase.")
        print("   Bot will trade when strong directional signals appear.")

if __name__ == "__main__":
    main()
