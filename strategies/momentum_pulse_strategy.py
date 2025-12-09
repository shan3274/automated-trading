"""
Momentum Pulse Strategy - fast entry when flat, follows short-term momentum
"""
import pandas as pd
import ta
from strategies.base_strategy import BaseStrategy, Signal
from utils.logger import setup_logger

logger = setup_logger('MomentumPulseStrategy')

class MomentumPulseStrategy(BaseStrategy):
    """Aggressive momentum follower for quick entries when flat"""

    def __init__(self):
        super().__init__('Momentum Pulse Strategy')
        self.rsi_period = 6
        self.ema_short = 3
        self.ema_long = 8
        logger.info("🚀 Momentum Pulse Strategy initialized (fast entries when flat)")

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df['ema_short'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=self.ema_short
        ).ema_indicator()

        df['ema_long'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=self.ema_long
        ).ema_indicator()

        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'],
            window=self.rsi_period
        ).rsi()

        if 'volume' not in df.columns:
            df['volume'] = 0

        df['vol_sma'] = df['volume'].rolling(window=5).mean()
        return df

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        df = self.calculate_indicators(df)
        if df.empty or len(df) < self.ema_long + 2:
            return Signal.HOLD

        last = df.iloc[-1]
        prev = df.iloc[-2]

        bullish_trend = last['ema_short'] > last['ema_long'] and last['close'] > last['ema_long']
        momentum_push = last['close'] > prev['close'] and prev['close'] > df.iloc[-3]['close']
        rsi_ok = last['rsi'] > 55

        vol_sma = last.get('vol_sma', 0) or 0
        volume_push = False
        if vol_sma > 0:
            volume_push = last['volume'] >= vol_sma * 1.1

        logger.info(
            f"📊 Pulse - Close: {last['close']:.4f}, RSI: {last['rsi']:.2f}, "
            f"EMA{self.ema_short}:{last['ema_short']:.4f}, EMA{self.ema_long}:{last['ema_long']:.4f}, "
            f"VolPush: {volume_push}"
        )

        if self.position is None:
            if bullish_trend and rsi_ok and (momentum_push or volume_push):
                logger.info("🟢 Pulse BUY - fast entry while flat")
                return Signal.BUY

        if self.position == 'LONG':
            if last['close'] < last['ema_short'] or last['rsi'] < 45:
                logger.info("🔴 Pulse SELL - momentum fading")
                return Signal.SELL

        return Signal.HOLD
