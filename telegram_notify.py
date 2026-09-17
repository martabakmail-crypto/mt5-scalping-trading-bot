import logging
import requests
from typing import Optional
from config import BotConfig

logger = logging.getLogger("ScalpingBot.Telegram")

class TelegramNotifier:
    """Client for pushing Telegram notifications and handling alerts."""

    def __init__(self, config: BotConfig):
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.enabled = config.ENABLE_TELEGRAM and bool(self.token) and bool(self.chat_id)
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage" if self.token else ""

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send message to specified Telegram chat."""
        if not self.enabled:
            logger.info(f"[Telegram Disabled] Message: {text}")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        try:
            res = requests.post(self.api_url, json=payload, timeout=10)
            if res.status_code == 200:
                return True
            else:
                logger.error(f"Telegram API Error ({res.status_code}): {res.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    def notify_order_opened(
        self,
        symbol: str,
        signal: str,
        lot: float,
        entry: float,
        sl: float,
        tp: float,
        score: float,
        ai_reasoning: str = ""
    ):
        """Alert when new trade is opened."""
        ai_text = f"\n🤖 *AI Advisor:* _{ai_reasoning}_" if ai_reasoning else ""
        msg = (
            f"🚀 *ORDER EXECUTED ({signal})*\n\n"
            f"📌 *Symbol:* `{symbol}`\n"
            f"📊 *Signal Confidence:* `{score:.1f}%` \n"
            f"📦 *Lot Size:* `{lot}`\n"
            f"💵 *Entry Price:* `{entry}`\n"
            f"🛑 *Stop Loss:* `{sl}`\n"
            f"🎯 *Take Profit:* `{tp}`\n"
            f"⏰ *Timeframe:* `M5`"
            f"{ai_text}"
        )
        self.send_message(msg)

    def notify_order_closed(
        self, symbol: str, ticket: int, profit: float, comment: str = ""
    ):
        """Alert when trade is closed."""
        icon = "🎉" if profit >= 0 else "🔻"
        msg = (
            f"{icon} *ORDER CLOSED*\n\n"
            f"📌 *Symbol:* `{symbol}` | Ticket: `{ticket}`\n"
            f"💰 *Profit/Loss:* `{profit:+.2f} Cent`\n"
            f"📝 *Reason:* `{comment or 'TP/SL Hit'}`"
        )
        self.send_message(msg)

    def notify_bot_status(self, balance: float, equity: float, active_trades: int):
        """Report bot status summary."""
        msg = (
            f"🤖 *SCALPING BOT STATUS REPORT*\n\n"
            f"💳 *Balance:* `{balance:.2f} Cents`\n"
            f"📈 *Equity:* `{equity:.2f} Cents`\n"
            f"🔄 *Active Trades:* `{active_trades}`\n"
            f"⚡ *System:* `ONLINE (Running M5 Engine)`"
        )
        self.send_message(msg)
