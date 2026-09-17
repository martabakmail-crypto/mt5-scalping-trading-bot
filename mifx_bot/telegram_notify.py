import requests
from config import MIFXConfig

class TelegramNotifier:
    """Telegram Push Notification Alerts for MIFX Bot."""

    def __init__(self, config: MIFXConfig):
        self.config = config
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, text: str) -> bool:
        if not self.config.ENABLE_TELEGRAM or not self.token or not self.chat_id:
            return False
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            res = requests.post(self.base_url, json=payload, timeout=10)
            return res.status_code == 200
        except Exception as e:
            print(f"Telegram alert error: {e}")
            return False

    def notify_order_opened(self, order_type: str, symbol: str, price: float, lot: float, sl: float, tp: float):
        emoji = "🚀 *AUTO BUY (MIFX)*" if order_type == "BUY" else "🔻 *AUTO SELL (MIFX)*"
        msg = (
            f"{emoji}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Broker:* MIFX (Monex)\n"
            f"🪙 *Symbol:* `{symbol}`\n"
            f"📦 *Lot Size:* `{lot}`\n"
            f"💵 *Entry Price:* `${price:,.2f}`\n"
            f"🛡️ *Auto SL:* `${sl:,.2f}`\n"
            f"🏆 *Auto TP:* `${tp:,.2f}`\n"
            f"🔐 *Protection:* 100% Attached on Entry\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )
        self.send_message(msg)

    def notify_trailing_update(self, ticket: int, symbol: str, new_sl: float):
        msg = (
            f"🔄 *TRAILING STOP UPDATED (MIFX)*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🎫 *Ticket:* `#{ticket}`\n"
            f"🪙 *Symbol:* `{symbol}`\n"
            f"🛡️ *New Stop Loss:* `${new_sl:,.2f}`\n"
            f"🔒 *Profit Locked Risk-Free!*\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )
        self.send_message(msg)

    def notify_status(self, symbol: str, current_price: float):
        msg = (
            f"🤖 *MIFX Scalping Bot Active*\n"
            f"📌 *Broker Server:* `{self.config.MIFX_SERVER}`\n"
            f"🪙 *Symbol:* `{symbol}`\n"
            f"📈 *Current Price:* `${current_price:,.2f}`\n"
            f"🛡️ *Auto SL/TP:* Active (1.5x ATR SL / 2.25x ATR TP)\n"
            f"🟢 *Status:* Scanning Market..."
        )
        self.send_message(msg)
