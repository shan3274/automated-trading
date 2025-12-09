"""
Multi-Timeframe Impulse Strategy
- Uses higher timeframe (HTF) trend filter
- Enters on lower timeframe (LTF) momentum, so trades are both aligned and frequent
"""
import pandas as pd
import ta
from strategies.base_strategy import BaseStrategy, Signal
from utils.logger import setup_logger

logger = setup_logger('MTFImpulseStrategy')

class MTFImpulseStrategy(BaseStrategy):
    """HTF trend + LTF momentum alignment"""
    requires_multi_tf = True
    htf_interval = '1h'   # Higher timeframe for trend
    ltf_interval = '5m'   # Lower timeframe for entries

    def __init__(self):
        super().__init__('MTF Impulse Strategy')
        # HTF filters (stable trend)
        self.htf_rsi_period = 14
        self.htf_ema_fast = 21
        self.htf_ema_slow = 50
        # LTF momentum (fast entries)
        self.ltf_rsi_period = 7
        self.ltf_ema_fast = 5
        self.ltf_ema_slow = 13
        logger.info("🧭 MTF Impulse initialized (HTF trend + LTF momentum)")

    def _prep_htf(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ema_fast'] = ta.trend.EMAIndicator(close=df['close'], window=self.htf_ema_fast).ema_indicator()
        df['ema_slow'] = ta.trend.EMAIndicator(close=df['close'], window=self.htf_ema_slow).ema_indicator()
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=self.htf_rsi_period).rsi()
        return df

    def _prep_ltf(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ema_fast'] = ta.trend.EMAIndicator(close=df['close'], window=self.ltf_ema_fast).ema_indicator()
        df['ema_slow'] = ta.trend.EMAIndicator(close=df['close'], window=self.ltf_ema_slow).ema_indicator()
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=self.ltf_rsi_period).rsi()
        if 'volume' not in df.columns:
            df['volume'] = 0
        df['vol_sma'] = df['volume'].rolling(window=8).mean()
        return df

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Required by BaseStrategy - for single-TF fallback"""
        return self._prep_ltf(df)

    def _htf_bias(self, df: pd.DataFrame):
        last = df.iloc[-1]
        fast = last['ema_fast']
        slow = last['ema_slow']
        rsi = last['rsi']
        if pd.isna(fast) or pd.isna(slow) or pd.isna(rsi):
            return None
        # Slightly lenient to allow trades: require trend + mild RSI confirmation
        if fast > slow and rsi > 45:
            return 'LONG'
        if fast < slow and rsi < 55:
            return 'SHORT'
        return None

    def generate_signal(self, data) -> Signal:
        df_htf = data.get('htf')
        df_ltf = data.get('ltf')
        if df_htf is None or df_ltf is None:
            return Signal.HOLD

        df_htf = self._prep_htf(df_htf)
        df_ltf = self._prep_ltf(df_ltf)

        if df_htf.empty or df_ltf.empty or len(df_ltf) < 3:
            return Signal.HOLD

        bias = self._htf_bias(df_htf)
        last_ltf = df_ltf.iloc[-1]
        prev_ltf = df_ltf.iloc[-2]
        price = last_ltf['close']

        # LTF momentum signals
        momentum_push = price > prev_ltf['close'] and prev_ltf['close'] > df_ltf.iloc[-3]['close']
        ema_trend_up = last_ltf['ema_fast'] > last_ltf['ema_slow']
        ema_trend_down = last_ltf['ema_fast'] < last_ltf['ema_slow']
        rsi_bull = last_ltf['rsi'] > 50
        rsi_bear = last_ltf['rsi'] < 50

        vol_sma = last_ltf.get('vol_sma', 0) or 0
        volume_push = False
        if vol_sma > 0:
            volume_push = last_ltf['volume'] >= vol_sma * 1.02

        # Decide using bias
        if bias == 'LONG':
            if ema_trend_up and (momentum_push or volume_push or rsi_bull):
                logger.info("🟢 MTF BUY (HTF up, LTF momentum)")
                return Signal.BUY
        elif bias == 'SHORT':
            if ema_trend_down and (momentum_push or volume_push or rsi_bear):
                logger.info("🔴 MTF SELL (HTF down, LTF momentum)")
                return Signal.SELL

        return Signal.HOLD
