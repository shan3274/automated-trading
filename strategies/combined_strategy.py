"""
Combined Strategy - Uses multiple indicators for confirmation
RSI + EMA Crossover for stronger signals
"""
import pandas as pd
import ta
from strategies.base_strategy import BaseStrategy, Signal
import config
from utils.logger import setup_logger

logger = setup_logger('CombinedStrategy')

class CombinedStrategy(BaseStrategy):
    """Combined RSI + EMA strategy for higher accuracy"""
    
    def __init__(self):
        super().__init__('Combined RSI + EMA Strategy')
        
        # RSI settings
        self.rsi_period = config.RSI_PERIOD
        self.rsi_overbought = config.RSI_OVERBOUGHT
        self.rsi_oversold = config.RSI_OVERSOLD
        
        # EMA settings
        self.ema_short = config.EMA_SHORT_PERIOD
        self.ema_long = config.EMA_LONG_PERIOD
        
        logger.info("📊 Combined Strategy initialized (RSI + EMA)")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators"""
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
        
        # MACD for additional confirmation
        macd = ta.trend.MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(close=df['close'])
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_lower'] = bollinger.bollinger_lband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Generate signal using multiple indicators"""
        df = self.calculate_indicators(df)
        
        if df.empty or len(df) < self.ema_long + 1:
            return Signal.HOLD
        
        # Current values
        current_rsi = df['rsi'].iloc[-1]
        current_price = df['close'].iloc[-1]
        current_short_ema = df['ema_short'].iloc[-1]
        current_long_ema = df['ema_long'].iloc[-1]
        current_macd = df['macd_histogram'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        
        # Previous values for crossover detection
        prev_short_ema = df['ema_short'].iloc[-2]
        prev_long_ema = df['ema_long'].iloc[-2]
        prev_macd = df['macd_histogram'].iloc[-2]
        
        # Count bullish signals
        bullish_signals = 0
        bearish_signals = 0
        
        # RSI conditions
        if current_rsi < self.rsi_oversold:
            bullish_signals += 1
        elif current_rsi > self.rsi_overbought:
            bearish_signals += 1
        
        # EMA crossover
        if prev_short_ema <= prev_long_ema and current_short_ema > current_long_ema:
            bullish_signals += 1
        elif prev_short_ema >= prev_long_ema and current_short_ema < current_long_ema:
            bearish_signals += 1
        
        # EMA trend
        if current_short_ema > current_long_ema:
            bullish_signals += 0.5
        else:
            bearish_signals += 0.5
        
        # MACD
        if prev_macd < 0 and current_macd > 0:
            bullish_signals += 1
        elif prev_macd > 0 and current_macd < 0:
            bearish_signals += 1
        
        # Bollinger Bands
        if current_price < bb_lower:
            bullish_signals += 0.5
        elif current_price > bb_upper:
            bearish_signals += 0.5
        
        # Log current indicators
        logger.info(f"📊 Indicators: RSI={current_rsi:.2f}, EMA Short={current_short_ema:.2f}, EMA Long={current_long_ema:.2f}")
        logger.info(f"📊 Signals Count: Bullish={bullish_signals}, Bearish={bearish_signals}")
        
        # Need at least 2 confirming signals
        if bullish_signals >= 2 and self.position is None:
            logger.info(f"🟢 STRONG BUY SIGNAL - {bullish_signals} indicators confirm")
            return Signal.BUY
        
        if bearish_signals >= 2 and self.position == 'LONG':
            logger.info(f"🔴 STRONG SELL SIGNAL - {bearish_signals} indicators confirm")
            return Signal.SELL
        
        return Signal.HOLD
