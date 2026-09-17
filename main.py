import time
import logging
import pandas as pd
from typing import Optional

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("Warning: MetaTrader5 package is not installed or not supported on this platform.")

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BotConfig
from signal_engine import SignalEngine
from risk_manager import RiskManager
from telegram_notify import TelegramNotifier
from ai_filter import AIMarketFilter


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("scalping_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ScalpingBot.Main")

class ScalpingBotEngine:
    """Main execution engine for MT5 Scalping Bot with AI Filter."""

    def __init__(self, config: BotConfig):
        self.config = config
        self.signal_engine = SignalEngine(config)
        self.risk_manager = RiskManager(config)
        self.telegram = TelegramNotifier(config)
        self.ai_filter = AIMarketFilter(config)
        self.is_running = True

    def initialize_mt5(self) -> bool:
        """Connect to MT5 Terminal."""
        if not MT5_AVAILABLE:
            logger.error("MetaTrader5 library is missing.")
            return False

        init_kwargs = {}
        if self.config.MT5_PATH:
            init_kwargs["path"] = self.config.MT5_PATH

        if not mt5.initialize(**init_kwargs):
            logger.warning(f"MT5 initialize failed: {mt5.last_error()}.")
            logger.info("Retrying MT5 connection or running in paper trading/mock mode...")
            # For demonstration & market simulation when standalone MT5 terminal GUI is not available
            return False


        if self.config.MT5_LOGIN > 0 and self.config.MT5_PASSWORD and self.config.MT5_SERVER:
            authorized = mt5.login(
                login=self.config.MT5_LOGIN,
                password=self.config.MT5_PASSWORD,
                server=self.config.MT5_SERVER
            )
            if not authorized:
                logger.error(f"MT5 Login failed: {mt5.last_error()}")
                return False
            logger.info(f"Successfully logged into MT5 Server: {self.config.MT5_SERVER}")

        # Check symbol selection
        symbol_info = mt5.symbol_info(self.config.SYMBOL)
        if symbol_info is None:
            logger.error(f"Symbol '{self.config.SYMBOL}' not found. Make sure symbol is in Market Watch.")
            return False

        if not symbol_info.visible:
            if not mt5.symbol_select(self.config.SYMBOL, True):
                logger.error(f"Failed to enable symbol '{self.config.SYMBOL}' in Market Watch.")
                return False

        terminal_info = mt5.terminal_info()
        logger.info(f"MT5 Connected! Terminal build: {terminal_info.build}, Connected: {terminal_info.connected}")
        return True

    def fetch_candle_data(self, num_candles: int = 300) -> Optional[pd.DataFrame]:
        """Fetch historical M5 candles from MT5."""
        if not MT5_AVAILABLE:
            return None

        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1
        }
        timeframe_mt5 = tf_map.get(self.config.TIMEFRAME, mt5.TIMEFRAME_M5)

        rates = mt5.copy_rates_from_pos(self.config.SYMBOL, timeframe_mt5, 0, num_candles)
        if rates is None or len(rates) == 0:
            logger.error(f"Failed to fetch rates for {self.config.SYMBOL}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_open_positions(self):
        """Retrieve open positions for current symbol."""
        if not MT5_AVAILABLE:
            return []
        positions = mt5.positions_get(symbol=self.config.SYMBOL)
        return positions if positions else []

    def execute_trade(self, signal: str, confidence_score: float, details: dict):
        """Send BUY or SELL order to MT5 with ATR TP/SL and AI validation."""
        if not MT5_AVAILABLE:
            return

        # 1. AI Market Filter Verification
        ai_approved, ai_reasoning = self.ai_filter.verify_trade(
            symbol=self.config.SYMBOL,
            signal=signal,
            confidence_score=confidence_score,
            details=details
        )

        if not ai_approved:
            logger.warning(f"Trade Rejected by AI Advisor! Reason: {ai_reasoning}")
            return

        symbol_info = mt5.symbol_info(self.config.SYMBOL)
        account_info = mt5.account_info()

        # 2. Spread check
        valid_spread, spread_pts = self.risk_manager.is_spread_valid(symbol_info)
        if not valid_spread:
            logger.warning(f"Trade skipped due to high spread ({spread_pts} pts).")
            return

        # 3. Calculate lot size & TP/SL
        lot = self.risk_manager.calculate_lot_size(account_info, symbol_info)
        point = symbol_info.point
        current_price = symbol_info.ask if signal == "BUY" else symbol_info.bid
        atr_value = details.get("atr_value", 0.001)

        sl_price, tp_price = self.risk_manager.calculate_tp_sl(signal, current_price, atr_value, point)
        order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config.SYMBOL,
            "volume": lot,
            "type": order_type,
            "price": current_price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": 10,
            "magic": 777123,
            "comment": f"ScalpBot_AI_{self.config.TIMEFRAME}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(
                f"ORDER PLACED ({signal})! Symbol: {self.config.SYMBOL}, Lot: {lot}, "
                f"Entry: {current_price}, SL: {sl_price}, TP: {tp_price}, Score: {confidence_score:.1f}%"
            )
            self.telegram.notify_order_opened(
                symbol=self.config.SYMBOL,
                signal=signal,
                lot=lot,
                entry=current_price,
                sl=sl_price,
                tp=tp_price,
                score=confidence_score,
                ai_reasoning=ai_reasoning
            )
        else:
            err_code = result.retcode if result else 'No Response'
            logger.error(f"Order Execution Failed! Retcode: {err_code}, Error: {mt5.last_error()}")

    def update_trailing_stops(self):
        """Update trailing stop for open positions."""
        if not MT5_AVAILABLE or not self.config.USE_TRAILING_STOP:
            return

        positions = self.get_open_positions()
        if not positions:
            return

        df = self.fetch_candle_data(50)
        if df is None:
            return

        df_calc = self.signal_engine.calculate_indicators(df)
        atr_val = df_calc.iloc[-1]['atr']
        symbol_info = mt5.symbol_info(self.config.SYMBOL)
        if not symbol_info:
            return

        for pos in positions:
            current_price = symbol_info.bid if pos.type == 0 else symbol_info.ask
            new_sl = self.risk_manager.calculate_trailing_stop(pos, current_price, atr_val, symbol_info.point)

            if new_sl is not None and new_sl != pos.sl:
                req = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": self.config.SYMBOL,
                    "position": pos.ticket,
                    "sl": new_sl,
                    "tp": pos.tp
                }
                res = mt5.order_send(req)
                if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"Trailing SL updated for Ticket #{pos.ticket} -> New SL: {new_sl}")

    def run_engine_cycle(self):
        """Single poll loop cycle."""
        positions = self.get_open_positions()

        # Update trailing stops for open trades
        if positions:
            self.update_trailing_stops()

        # Limit concurrent trades (single trade strategy)
        if len(positions) >= 1:
            return

        df = self.fetch_candle_data(300)
        if df is None or len(df) < self.config.EMA_SLOW_PERIOD:
            return

        signal, score, details = self.signal_engine.evaluate_signal(df)

        if signal in ["BUY", "SELL"] and score >= self.config.MIN_SIGNAL_CONFIDENCE:
            logger.info(f"SIGNAL GENERATED: {signal} | Confidence: {score:.1f}% | Details: {details}")
            self.execute_trade(signal, score, details)

    def start(self):
        """Start the trading bot loop."""
        logger.info("Initializing Scalping Trading Bot Engine with AI Filter...")

        while self.is_running and not self.initialize_mt5():
            logger.warning("MT5 initialize pending (waiting for MT5 Terminal process). Retrying in 15 seconds...")
            time.sleep(15)

        if not self.is_running:
            return

        logger.info(
            f"Bot Engine Active! Symbol: {self.config.SYMBOL}, Timeframe: {self.config.TIMEFRAME}, "
            f"Min Confidence: {self.config.MIN_SIGNAL_CONFIDENCE}%, AI Filter: {self.config.USE_AI_FILTER}"
        )


        acc = mt5.account_info()
        if acc:
            self.telegram.notify_bot_status(acc.balance, acc.equity, len(self.get_open_positions()))

        try:
            while self.is_running:
                self.run_engine_cycle()
                time.sleep(self.config.POLL_INTERVAL_SEC)
        except KeyboardInterrupt:
            logger.info("Bot manually stopped by user.")
        finally:
            if MT5_AVAILABLE:
                mt5.shutdown()
            logger.info("MT5 Engine Shutdown Completed.")

if __name__ == "__main__":
    bot_config = BotConfig()
    bot = ScalpingBotEngine(bot_config)
    bot.start()
