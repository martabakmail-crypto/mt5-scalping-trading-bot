import logging
from typing import Tuple, Optional, Dict, Any
from config import BotConfig

logger = logging.getLogger("ScalpingBot.RiskManager")

class RiskManager:
    """Handles position sizing, stop loss, take profit, trailing stops, and spread guards."""

    def __init__(self, config: BotConfig):
        self.config = config

    def is_spread_valid(self, symbol_info: Any) -> Tuple[bool, float]:
        """Check if current spread (in points) is within safe limits."""
        if symbol_info is None:
            return False, 0.0

        spread_points = float(symbol_info.spread)
        if spread_points > self.config.MAX_SPREAD_POINTS:
            logger.warning(
                f"Spread too high for {symbol_info.name}: {spread_points} points "
                f"(Max allowed: {self.config.MAX_SPREAD_POINTS})"
            )
            return False, spread_points
        return True, spread_points

    def calculate_lot_size(self, account_info: Any, symbol_info: Any) -> float:
        """Calculate cent lot size (Fixed or Dynamic based on equity)."""
        if not self.config.USE_DYNAMIC_LOT or account_info is None:
            return self.config.DEFAULT_LOT

        # Dynamic risk calculation (e.g. 1% of account balance)
        balance = account_info.balance
        risk_amount = balance * (self.config.RISK_PERCENT / 100.0)

        # Min and step lot bounds from broker
        min_lot = symbol_info.volume_min if symbol_info else 0.01
        max_lot = symbol_info.volume_max if symbol_info else 100.0
        step_lot = symbol_info.volume_step if symbol_info else 0.01

        # Basic dynamic lot estimation
        calculated_lot = round(risk_amount / 1000.0, 2)
        calculated_lot = max(min_lot, min(max_lot, calculated_lot))

        # Adjust to step lot
        steps = round(calculated_lot / step_lot)
        final_lot = steps * step_lot
        return round(final_lot, 2)

    def calculate_tp_sl(
        self, signal: str, entry_price: float, atr: float, point: float
    ) -> Tuple[float, float]:
        """Calculate absolute Stop Loss and Take Profit prices based on ATR."""
        sl_distance = max(atr * self.config.ATR_SL_MULTIPLIER, 10 * point)
        tp_distance = max(atr * self.config.ATR_TP_MULTIPLIER, 15 * point)

        if signal == "BUY":
            sl_price = entry_price - sl_distance
            tp_price = entry_price + tp_distance
        else:  # SELL
            sl_price = entry_price + sl_distance
            tp_price = entry_price - tp_distance

        return round(sl_price, 5), round(tp_price, 5)

    def calculate_trailing_stop(
        self,
        position: Any,
        current_price: float,
        atr: float,
        point: float
    ) -> Optional[float]:
        """
        Calculate updated Stop Loss for active positions (Breakeven & Dynamic Trailing).
        Returns new SL price if SL needs updating, otherwise None.
        """
        if not self.config.USE_TRAILING_STOP or atr <= 0:
            return None

        pos_type = position.type  # 0 for BUY, 1 for SELL
        open_price = position.open_price
        current_sl = position.sl
        digits = position.digits if hasattr(position, 'digits') else 5

        breakeven_dist = atr * self.config.BREAKEVEN_TRIGGER_ATR
        trailing_step = atr * self.config.TRAILING_STEP_ATR

        if pos_type == 0:  # BUY Position
            profit_dist = current_price - open_price
            if profit_dist >= breakeven_dist:
                # Target SL: Lock in profit at open_price + trailing_step
                new_sl = open_price + (profit_dist - trailing_step)
                # Ensure new SL moves upward only and above open_price
                if new_sl > current_sl and new_sl > open_price:
                    return round(new_sl, digits)

        elif pos_type == 1:  # SELL Position
            profit_dist = open_price - current_price
            if profit_dist >= breakeven_dist:
                # Target SL: Lock in profit at open_price - (profit_dist - trailing_step)
                new_sl = open_price - (profit_dist - trailing_step)
                # Ensure new SL moves downward only and below open_price
                if current_sl == 0.0 or (new_sl < current_sl and new_sl < open_price):
                    return round(new_sl, digits)

        return None
