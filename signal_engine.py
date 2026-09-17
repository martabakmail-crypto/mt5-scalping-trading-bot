import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from config import BotConfig

class SignalEngine:
    """Calculates multi-indicator technical analysis and composite signal confidence score."""

    def __init__(self, config: BotConfig):
        self.config = config

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute EMA, RSI, ATR, and Candlestick features."""
        df = df.copy()

        # Fast and Slow Exponential Moving Averages
        df['ema_fast'] = df['close'].ewm(span=self.config.EMA_FAST_PERIOD, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.config.EMA_SLOW_PERIOD, adjust=False).mean()

        # Relative Strength Index (RSI)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.config.RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.config.RSI_PERIOD).mean()
        rs = gain / (loss.replace(0, np.nan))
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'] = df['rsi'].fillna(50)

        # Average True Range (ATR)
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=self.config.ATR_PERIOD).mean()
        df['atr'] = df['atr'].bfill()

        # Candlestick body and wicks
        df['body_size'] = (df['close'] - df['open']).abs()
        df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
        df['candle_range'] = df['high'] - df['low']

        return df

    def evaluate_signal(self, df: pd.DataFrame) -> Tuple[str, float, Dict[str, Any]]:
        """
        Evaluate market conditions on the latest completed candle.
        Returns: (Signal Direction 'BUY'/'SELL'/'NEUTRAL', Confidence Score %, Component Breakdown)
        """
        if len(df) < self.config.EMA_SLOW_PERIOD + 5:
            return "NEUTRAL", 0.0, {"reason": "Insufficient candle history"}

        df_calc = self.calculate_indicators(df)
        candle = df_calc.iloc[-1]  # Latest candle
        prev_candle = df_calc.iloc[-2]

        # Weights breakdown
        # Trend (30%), Momentum (25%), Price Action (25%), Volatility (20%)
        buy_score = 0.0
        sell_score = 0.0

        details = {}

        # 1. Trend Filter (30 Points)
        if candle['close'] > candle['ema_fast'] > candle['ema_slow']:
            buy_score += 30.0
            details['trend'] = "Strong Uptrend (Close > EMA50 > EMA200)"
        elif candle['close'] < candle['ema_fast'] < candle['ema_slow']:
            sell_score += 30.0
            details['trend'] = "Strong Downtrend (Close < EMA50 < EMA200)"
        elif candle['ema_fast'] > candle['ema_slow']:
            buy_score += 15.0
            details['trend'] = "Moderate Uptrend (EMA50 > EMA200)"
        elif candle['ema_fast'] < candle['ema_slow']:
            sell_score += 15.0
            details['trend'] = "Moderate Downtrend (EMA50 < EMA200)"
        else:
            details['trend'] = "Flat / Neutral Trend"

        # 2. Momentum Filter (RSI) (25 Points)
        if candle['rsi'] < self.config.RSI_OVERSOLD:
            buy_score += 25.0
            details['rsi'] = f"Oversold ({candle['rsi']:.1f})"
        elif candle['rsi'] > self.config.RSI_OVERBOUGHT:
            sell_score += 25.0
            details['rsi'] = f"Overbought ({candle['rsi']:.1f})"
        elif 40 <= candle['rsi'] <= 50 and candle['close'] > candle['ema_fast']:
            buy_score += 15.0
            details['rsi'] = f"Bullish Pullback RSI ({candle['rsi']:.1f})"
        elif 50 <= candle['rsi'] <= 60 and candle['close'] < candle['ema_fast']:
            sell_score += 15.0
            details['rsi'] = f"Bearish Pullback RSI ({candle['rsi']:.1f})"
        else:
            details['rsi'] = f"Neutral RSI ({candle['rsi']:.1f})"

        # 3. Price Action / Candlestick Rejection (25 Points)
        candle_range = candle['candle_range'] if candle['candle_range'] > 0 else 1.0
        lower_wick_ratio = candle['lower_wick'] / candle_range
        upper_wick_ratio = candle['upper_wick'] / candle_range

        # Bullish Rejection / Engulfing
        if lower_wick_ratio >= 0.4:
            buy_score += 25.0
            details['price_action'] = f"Bullish Wick Rejection ({lower_wick_ratio*100:.0f}%)"
        elif candle['close'] > candle['open'] and candle['body_size'] > prev_candle['body_size']:
            buy_score += 20.0
            details['price_action'] = "Bullish Engulfing Body"

        # Bearish Rejection / Engulfing
        if upper_wick_ratio >= 0.4:
            sell_score += 25.0
            details['price_action'] = f"Bearish Wick Rejection ({upper_wick_ratio*100:.0f}%)"
        elif candle['close'] < candle['open'] and candle['body_size'] > prev_candle['body_size']:
            sell_score += 20.0
            details['price_action'] = "Bearish Engulfing Body"

        # 4. Volatility (ATR Filter) (20 Points)
        avg_atr = df_calc['atr'].tail(20).mean()
        if candle['atr'] >= avg_atr * 0.9:
            # Good trading volatility
            buy_score += 20.0
            sell_score += 20.0
            details['volatility'] = f"Optimal ATR ({candle['atr']:.4f})"
        else:
            details['volatility'] = f"Low Volatility ATR ({candle['atr']:.4f})"

        details['atr_value'] = candle['atr']
        details['current_price'] = candle['close']

        # Determine winner
        if buy_score >= sell_score and buy_score >= self.config.MIN_SIGNAL_CONFIDENCE:
            return "BUY", buy_score, details
        elif sell_score > buy_score and sell_score >= self.config.MIN_SIGNAL_CONFIDENCE:
            return "SELL", sell_score, details

        highest_score = max(buy_score, sell_score)
        return "NEUTRAL", highest_score, details
