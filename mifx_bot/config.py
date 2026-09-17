import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class MIFXConfig:
    """MIFX (Monex Investindo Futures) Bot Configuration."""
    # MIFX Login Credentials
    MIFX_LOGIN: int = int(os.getenv("MIFX_LOGIN", "0"))
    MIFX_PASSWORD: str = os.getenv("MIFX_PASSWORD", "")
    MIFX_SERVER: str = os.getenv("MIFX_SERVER", "Monex-Demo")  # Monex-Demo or Monex-Live

    # Trading Symbol & Timeframe
    SYMBOL: str = os.getenv("SYMBOL", "XAUUSD")  # XAUUSD (Gold), EURUSD, GBPUSD
    TIMEFRAME: str = os.getenv("TIMEFRAME", "M5")  # M5 Scalping

    # Signal Thresholds
    MIN_SIGNAL_CONFIDENCE: float = float(os.getenv("MIN_SIGNAL_CONFIDENCE", "70.0"))

    # Indicator Parameters
    EMA_FAST_PERIOD: int = 50
    EMA_SLOW_PERIOD: int = 200
    RSI_PERIOD: int = 14
    RSI_OVERSOLD: float = 35.0
    RSI_OVERBOUGHT: float = 65.0
    ATR_PERIOD: int = 14

    # Risk Management Settings (Auto SL / TP / Trailing)
    DEFAULT_LOT: float = float(os.getenv("DEFAULT_LOT", "0.1"))  # MIFX Standard Lot (0.1 min for gold)
    MAX_SPREAD_POINTS: float = float(os.getenv("MAX_SPREAD_POINTS", "50.0"))

    # ATR SL / TP Multipliers
    ATR_SL_MULTIPLIER: float = 1.5   # Auto SL = 1.5 * ATR
    ATR_TP_MULTIPLIER: float = 2.25  # Auto TP = 2.25 * ATR (Risk:Reward ~ 1:1.5)

    # Trailing Stop & Breakeven Settings
    USE_TRAILING_STOP: bool = True
    BREAKEVEN_TRIGGER_ATR: float = 1.0  # Move SL to breakeven when profit >= 1.0 * ATR
    TRAILING_STEP_ATR: float = 0.5      # Trail SL every 0.5 * ATR

    # Telegram Settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "8944375033:AAEXvUUu1osAqL56p4XN5R1AFmsL6LOV970")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "151562975")
    ENABLE_TELEGRAM: bool = os.getenv("ENABLE_TELEGRAM", "true").lower() == "true"

    # Engine Loop Interval (seconds)
    POLL_INTERVAL_SEC: int = 5
