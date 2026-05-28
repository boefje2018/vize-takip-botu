import os
import httpx


class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
        self.enabled = bool(self.bot_token and self.chat_id)

    def send(self, message: str) -> bool:
        if not self.enabled:
            return False
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    f"{self.api_base}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": False,
                    },
                )
            return resp.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
