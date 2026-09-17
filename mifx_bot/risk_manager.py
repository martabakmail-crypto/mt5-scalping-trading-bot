from config import MIFXConfig

class RiskManager:
    """Risk Management Engine for MIFX: Auto SL, Auto TP, Breakeven, and Trailing Stop."""

    def __init__(self, config: MIFXConfig):
        self.config = config

    def calculate_sl_tp(self, entry_price: float, atr_value: float, order_type: str) -> tuple[float, float]:
        """Calculate Auto SL and Auto TP prices based on ATR volatility."""
        sl_distance = atr_value * self.config.ATR_SL_MULTIPLIER
        tp_distance = atr_value * self.config.ATR_TP_MULTIPLIER

        if order_type == "BUY":
            sl_price = round(entry_price - sl_distance, 2)
            tp_price = round(entry_price + tp_distance, 2)
        else:  # SELL
            sl_price = round(entry_price + sl_distance, 2)
            tp_price = round(entry_price - tp_distance, 2)

        return sl_price, tp_price

    def calculate_trailing_stop(self, pos_type: str, open_price: float, current_sl: float, current_price: float, atr_val: float) -> tuple[float, bool]:
        """
        Calculate updated trailing stop loss price.
        Returns (new_sl, is_updated).
        """
        if not self.config.USE_TRAILING_STOP or atr_val <= 0:
            return current_sl, False

        breakeven_dist = atr_val * self.config.BREAKEVEN_TRIGGER_ATR
        trailing_step = atr_val * self.config.TRAILING_STEP_ATR

        new_sl = current_sl
        updated = False

        if pos_type == "BUY":
            profit_dist = current_price - open_price
            # Breakeven check
            if profit_dist >= breakeven_dist and current_sl < open_price:
                new_sl = round(open_price, 2)
                updated = True
            # Trailing stop check
            elif profit_dist >= breakeven_dist:
                proposed_sl = round(current_price - trailing_step, 2)
                if proposed_sl > current_sl:
                    new_sl = proposed_sl
                    updated = True

        elif pos_type == "SELL":
            profit_dist = open_price - current_price
            # Breakeven check
            if profit_dist >= breakeven_dist and (current_sl == 0 or current_sl > open_price):
                new_sl = round(open_price, 2)
                updated = True
            # Trailing stop check
            elif profit_dist >= breakeven_dist:
                proposed_sl = round(current_price + trailing_step, 2)
                if current_sl == 0 or proposed_sl < current_sl:
                    new_sl = proposed_sl
                    updated = True

        return new_sl, updated
