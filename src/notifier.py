"""Telegram notifications for price updates"""

import requests
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends price update notifications via Telegram Bot API"""

    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier

        Args:
            bot_token: Telegram bot API token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        logger.info(f"Initialized Telegram notifier for chat: {chat_id}")

    def send_price_update(
        self,
        current_price: Decimal,
        url: str,
        last_price: Optional[float] = None,
    ) -> bool:
        """
        Send price update notification to Telegram

        Args:
            current_price: Current price value
            url: Product URL
            last_price: Previous price for comparison (optional)

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            # Calculate price change if previous price exists
            if last_price is not None:
                change = float(current_price) - last_price
                change_pct = (change / last_price) * 100

                if change > 0:
                    trend = "📈"
                    change_text = f"+{change:.2f} ({change_pct:+.1f}%)"
                elif change < 0:
                    trend = "📉"
                    change_text = f"{change:.2f} ({change_pct:.1f}%)"
                else:
                    trend = "➡️"
                    change_text = "No change"
            else:
                trend = "🆕"
                change_text = "First check"

            # Format message with HTML
            message = f"""
{trend} <b>Price Update</b>

Current Price: <b>{float(current_price):.2f}</b>
Change: {change_text}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

<a href="{url}">View Product</a>
            """.strip()

            return self._send_message(message)

        except Exception as e:
            logger.error(f"Error creating price update message: {e}")
            return False

    def send_error(self, error_message: str) -> bool:
        """
        Send error notification to Telegram

        Args:
            error_message: Error description

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            message = f"❌ <b>Price Tracker Error</b>\n\n{error_message}"
            return self._send_message(message)

        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False

    def _send_message(self, message: str) -> bool:
        """
        Send message to Telegram via Bot API

        Args:
            message: Message text (HTML formatted)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending message to Telegram chat: {self.chat_id}")

            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=10,
            )

            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info("Message sent successfully to Telegram")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test Telegram bot connection

        Returns:
            True if bot is working, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info(
                    f"Telegram bot test successful: {result['result']['username']}"
                )
                return True
            else:
                logger.error(f"Telegram bot test failed: {result}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
