import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class BotConfig:
    """Bot Configuration settings."""
    # MT5 Credentials
    MT5_LOGIN: int = int(os.getenv("MT5_LOGIN", "0"))
    MT5_PASSWORD: str = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER: str = os.getenv("MT5_SERVER", "")
    MT5_PATH: Optional[str] = os.getenv("MT5_PATH", None)  # Path to terminal64.exe if non-standard

    # Trading Symbol & Timeframe
    SYMBOL: str = os.getenv("SYMBOL", "XAUUSDc")  # Default Cent Symbol (e.g. XAUUSDc, EURUSDc)
    TIMEFRAME: str = os.getenv("TIMEFRAME", "M5")  # Default M5 Timeframe

    # Signal Thresholds
    MIN_SIGNAL_CONFIDENCE: float = float(os.getenv("MIN_SIGNAL_CONFIDENCE", "70.0"))  # Min 70% confidence score

    # AI Market Sentiment Filter Settings (Google Gemini)
    USE_AI_FILTER: bool = os.getenv("USE_AI_FILTER", "false").lower() == "true"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "gemini-2.5-flash")

    # Indicator Parameters
    EMA_FAST_PERIOD: int = 50
    EMA_SLOW_PERIOD: int = 200
    RSI_PERIOD: int = 14
    RSI_OVERSOLD: float = 35.0
    RSI_OVERBOUGHT: float = 65.0
    ATR_PERIOD: int = 14

    # Risk Management Settings
    DEFAULT_LOT: float = float(os.getenv("DEFAULT_LOT", "0.01"))  # Cent lot size
    USE_DYNAMIC_LOT: bool = os.getenv("USE_DYNAMIC_LOT", "false").lower() == "true"
    RISK_PERCENT: float = float(os.getenv("RISK_PERCENT", "1.0"))  # 1% per trade if dynamic
    MAX_SPREAD_POINTS: float = float(os.getenv("MAX_SPREAD_POINTS", "50.0"))  # Max allowed spread in points

    # TP / SL Multipliers (ATR Based)
    ATR_SL_MULTIPLIER: float = 1.5   # Stop loss = 1.5 * ATR
    ATR_TP_MULTIPLIER: float = 2.25  # Take profit = 2.25 * ATR (Risk:Reward ~ 1:1.5)

    # Trailing Stop & Breakeven Settings
    USE_TRAILING_STOP: bool = True
    BREAKEVEN_TRIGGER_ATR: float = 1.0  # Move SL to breakeven when profit reaches 1.0 * ATR
    TRAILING_STEP_ATR: float = 0.5      # Trail SL every 0.5 * ATR

    # Telegram Settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    ENABLE_TELEGRAM: bool = os.getenv("ENABLE_TELEGRAM", "false").lower() == "true"

    # Engine Loop Interval (seconds)
    POLL_INTERVAL_SEC: int = 5
