"""
1-Minute Strategy - Fast trading on 1-minute candles
Aggressive strategy for quick testing and scalping
"""
import pandas as pd
import ta
from strategies.base_strategy import BaseStrategy, Signal
from utils.logger import setup_logger

logger = setup_logger('1MinStrategy')

class OneMinuteStrategy(BaseStrategy):
    """1-minute scalping strategy using RSI and EMA on 1m candles"""
    
    def __init__(self):
        super().__init__('1-Minute Fast Strategy')
        
        # More aggressive settings for 1-minute timeframe
        self.rsi_period = 7  # Shorter period for faster signals
        self.rsi_overbought = 65  # Lower threshold
        self.rsi_oversold = 35  # Higher threshold
        
        self.ema_short = 5  # Very short
        self.ema_long = 12  # Short
        
        logger.info("⚡ 1-Minute Strategy initialized")
        logger.info(f"   RSI: {self.rsi_period} period, OS: {self.rsi_oversold}, OB: {self.rsi_overbought}")
        logger.info(f"   EMA: {self.ema_short}/{self.ema_long}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate indicators for 1-minute data"""
        df = df.copy()
        
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'],
            window=self.rsi_period
        ).rsi()
        
        # EMAs
        df['ema_short'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=self.ema_short
        ).ema_indicator()
        
        df['ema_long'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=self.ema_long
        ).ema_indicator()
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Generate signal - more aggressive for 1-minute trading"""
        df = self.calculate_indicators(df)
        
        if df.empty or len(df) < self.ema_long + 1:
            return Signal.HOLD
        
        # Current values
        current_rsi = df['rsi'].iloc[-1]
        current_short_ema = df['ema_short'].iloc[-1]
        current_long_ema = df['ema_long'].iloc[-1]
        
        # Previous values
        prev_short_ema = df['ema_short'].iloc[-2]
        prev_long_ema = df['ema_long'].iloc[-2]
        
        # Count signals
        bullish = 0
        bearish = 0
        
        # RSI - more lenient thresholds
        if current_rsi < self.rsi_oversold:
            bullish += 1
        elif current_rsi > self.rsi_overbought:
            bearish += 1
        
        # EMA crossover
        if prev_short_ema <= prev_long_ema and current_short_ema > current_long_ema:
            bullish += 1
            logger.info("🟢 EMA Bullish Crossover detected!")
        elif prev_short_ema >= prev_long_ema and current_short_ema < current_long_ema:
            bearish += 1
            logger.info("🔴 EMA Bearish Crossover detected!")
        
        # EMA trend (partial weight)
        if current_short_ema > current_long_ema:
            bullish += 0.5
        else:
            bearish += 0.5
        
        logger.info(f"📊 1m Strategy - RSI: {current_rsi:.2f}, Bullish: {bullish}, Bearish: {bearish}")
        
        # Need only 1 strong signal for 1-minute trading
        if bullish >= 1.0 and self.position is None:
            logger.info(f"🟢 BUY SIGNAL - {bullish} signals")
            return Signal.BUY
        
        if bearish >= 1.0 and self.position == 'LONG':
            logger.info(f"🔴 SELL SIGNAL - {bearish} signals")
            return Signal.SELL
        
        return Signal.HOLD
