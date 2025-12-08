"""
RSI (Relative Strength Index) Trading Strategy
Buy when RSI < 30 (oversold), Sell when RSI > 70 (overbought)
"""
import pandas as pd
import ta
from strategies.base_strategy import BaseStrategy, Signal
import config
from utils.logger import setup_logger

logger = setup_logger('RSIStrategy')

class RSIStrategy(BaseStrategy):
    """RSI-based trading strategy"""
    
    def __init__(
        self, 
        period: int = None,
        overbought: int = None,
        oversold: int = None
    ):
        super().__init__('RSI Strategy')
        self.period = period or config.RSI_PERIOD
        self.overbought = overbought or config.RSI_OVERBOUGHT
        self.oversold = oversold or config.RSI_OVERSOLD
        
        logger.info(f"📊 RSI Strategy initialized - Period: {self.period}, "
                   f"Overbought: {self.overbought}, Oversold: {self.oversold}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI indicator"""
        df = df.copy()
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'],
            window=self.period
        ).rsi()
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Generate signal based on RSI"""
        df = self.calculate_indicators(df)
        
        if df.empty or len(df) < self.period:
            return Signal.HOLD
        
        current_rsi = df['rsi'].iloc[-1]
        prev_rsi = df['rsi'].iloc[-2] if len(df) > 1 else current_rsi
        
        logger.debug(f"RSI: {current_rsi:.2f}")
        
        # Buy signal: RSI crosses above oversold level
        if current_rsi < self.oversold and self.position is None:
            logger.info(f"🟢 BUY SIGNAL - RSI: {current_rsi:.2f} (Oversold)")
            return Signal.BUY
        
        # Sell signal: RSI crosses above overbought level
        if current_rsi > self.overbought and self.position == 'LONG':
            logger.info(f"🔴 SELL SIGNAL - RSI: {current_rsi:.2f} (Overbought)")
            return Signal.SELL
        
        return Signal.HOLD
