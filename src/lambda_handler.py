"""AWS Lambda handler for price tracker"""

import logging
import json
from datetime import datetime

from config import Config
from scraper import PriceScraper
from database import PriceDatabase
from notifier import TelegramNotifier
from models import PriceRecord

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda entry point triggered by EventBridge Scheduler

    Args:
        event: Lambda event object (from EventBridge)
        context: Lambda context object

    Returns:
        Dict with statusCode and body
    """
    try:
        logger.info("=" * 60)
        logger.info("Price Tracker Lambda function started")
        # logger.info(f"Request ID: {context.request_id if context else 'local'}")
        logger.info("=" * 60)

        # Load configuration from environment + SSM
        logger.info("Loading configuration...")
        config = Config.from_env()
        logger.info(f"Configuration loaded - Product URL: {config.PRODUCT_URL}")

        # Initialize components
        logger.info("Initializing components...")
        db = PriceDatabase(table_name=config.DYNAMODB_TABLE)
        scraper = PriceScraper(config.PRODUCT_URL, config.PRICE_SELECTOR)
        notifier = TelegramNotifier(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)

        # Scrape current price
        logger.info("Starting price scrape...")
        price, raw_text = scraper.scrape_price()
        logger.info(f"✓ Price scraped: {price}")

        # Get last price for comparison
        logger.info("Retrieving price history...")
        last_record = db.get_last_price()
        last_price = last_record.price if last_record else None

        if last_price:
            logger.info(f"Last recorded price: {last_price}")
        else:
            logger.info("No previous price records found (first check)")

        # Create new price record
        record = PriceRecord(
            timestamp=datetime.utcnow(),
            price=float(price),
            url=config.PRODUCT_URL,
            raw_text=raw_text,
        )

        # Store in DynamoDB
        logger.info("Storing price record in DynamoDB...")
        db.insert_price(record)
        logger.info("✓ Price record stored")

        # Send Telegram notification
        logger.info("Sending Telegram notification...")
        notification_sent = notifier.send_price_update(
            price, config.PRODUCT_URL, last_price
        )

        if notification_sent:
            logger.info("✓ Telegram notification sent")
        else:
            logger.warning("⚠ Telegram notification failed (check logs above)")

        # Prepare success response
        response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "price": float(price),
                    "timestamp": record.timestamp.isoformat(),
                    "previous_price": last_price,
                    "notification_sent": notification_sent,
                }
            ),
        }

        logger.info("=" * 60)
        logger.info("Price Tracker completed successfully")
        logger.info("=" * 60)

        return response

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ Price check failed: {str(e)}", exc_info=True)
        logger.error("=" * 60)

        # Try to send error notification
        try:
            logger.info("Attempting to send error notification...")
            config = Config.from_env()
            notifier = TelegramNotifier(
                config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID
            )
            notifier.send_error(f"Price check failed: {str(e)}")
            logger.info("Error notification sent")
        except Exception as notify_error:
            logger.error(f"Failed to send error notification: {notify_error}")

        # Return error response
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": str(e)}),
        }
