"""
EMA Crossover Trading Strategy
Buy when short EMA crosses above long EMA
Sell when short EMA crosses below long EMA
"""
import pandas as pd
import ta
from strategies.base_strategy import BaseStrategy, Signal
import config
from utils.logger import setup_logger

logger = setup_logger('EMACrossover')

class EMACrossoverStrategy(BaseStrategy):
    """EMA Crossover trading strategy"""
    
    def __init__(
        self,
        short_period: int = None,
        long_period: int = None
    ):
        super().__init__('EMA Crossover Strategy')
        self.short_period = short_period or config.EMA_SHORT_PERIOD
        self.long_period = long_period or config.EMA_LONG_PERIOD
        
        logger.info(f"📊 EMA Crossover Strategy initialized - "
                   f"Short: {self.short_period}, Long: {self.long_period}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMA indicators"""
        df = df.copy()
        
        df['ema_short'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=self.short_period
        ).ema_indicator()
        
        df['ema_long'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=self.long_period
        ).ema_indicator()
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Generate signal based on EMA crossover"""
        df = self.calculate_indicators(df)
        
        if df.empty or len(df) < self.long_period + 1:
            return Signal.HOLD
        
        # Current values
        current_short = df['ema_short'].iloc[-1]
        current_long = df['ema_long'].iloc[-1]
        
        # Previous values
        prev_short = df['ema_short'].iloc[-2]
        prev_long = df['ema_long'].iloc[-2]
        
        logger.debug(f"EMA Short: {current_short:.2f}, EMA Long: {current_long:.2f}")
        
        # Golden Cross: Short EMA crosses above Long EMA
        if prev_short <= prev_long and current_short > current_long:
            if self.position is None:
                logger.info(f"🟢 BUY SIGNAL - Golden Cross "
                           f"(EMA{self.short_period}: {current_short:.2f} > "
                           f"EMA{self.long_period}: {current_long:.2f})")
                return Signal.BUY
        
        # Death Cross: Short EMA crosses below Long EMA
        if prev_short >= prev_long and current_short < current_long:
            if self.position == 'LONG':
                logger.info(f"🔴 SELL SIGNAL - Death Cross "
                           f"(EMA{self.short_period}: {current_short:.2f} < "
                           f"EMA{self.long_period}: {current_long:.2f})")
                return Signal.SELL
        
        return Signal.HOLD
