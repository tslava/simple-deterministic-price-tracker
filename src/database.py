"""DynamoDB database operations for price history storage"""

import boto3
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from botocore.exceptions import ClientError

from models import PriceRecord

logger = logging.getLogger(__name__)


class PriceDatabase:
    """Manages price history storage in DynamoDB"""

    def __init__(
        self, table_name: str, product_id: str = "default", dynamodb_resource=None
    ):
        """
        Initialize database connection

        Args:
            table_name: Name of the DynamoDB table
            product_id: Identifier for the product (default: "default")
            dynamodb_resource: Optional boto3 DynamoDB resource (for testing/mocking)
        """
        self.product_id = product_id

        if dynamodb_resource is None:
            dynamodb_resource = boto3.resource("dynamodb")

        self.table = dynamodb_resource.Table(table_name)
        logger.info(f"Initialized DynamoDB connection to table: {table_name}")

    def insert_price(self, record: PriceRecord) -> None:
        """
        Insert a price record into DynamoDB

        Args:
            record: PriceRecord to store

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            item = {
                "product_id": self.product_id,
                "timestamp": record.timestamp.isoformat(),
                # DynamoDB uses Decimal for numbers, not float
                "price": Decimal(str(record.price)),
                "currency": record.currency,
                "url": record.url,
                "raw_text": record.raw_text,
            }

            self.table.put_item(Item=item)
            logger.info(
                f"Stored price in DynamoDB: {record.price} {record.currency} at {record.timestamp}"
            )

        except ClientError as e:
            logger.error(f"Failed to insert price record: {e}")
            raise

    def get_last_price(self) -> Optional[PriceRecord]:
        """
        Get the most recent price record for this product

        Returns:
            PriceRecord if found, None otherwise

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            # Query for this product_id, sorted by timestamp descending, limit 1
            response = self.table.query(
                KeyConditionExpression="product_id = :pid",
                ExpressionAttributeValues={":pid": self.product_id},
                Limit=1,
                ScanIndexForward=False,  # Descending order (latest first)
            )

            if response.get("Items"):
                item = response["Items"][0]
                record = PriceRecord(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    price=float(item["price"]),  # Convert Decimal back to float
                    currency=item["currency"],
                    url=item["url"],
                    raw_text=item["raw_text"],
                )
                logger.info(
                    f"Retrieved last price: {record.price} {record.currency} at {record.timestamp}"
                )
                return record

            logger.info("No previous price records found")
            return None

        except ClientError as e:
            logger.error(f"Failed to query last price: {e}")
            raise

    def get_price_history(self, limit: int = 30) -> List[PriceRecord]:
        """
        Get recent price history for this product

        Args:
            limit: Maximum number of records to retrieve (default: 30)

        Returns:
            List of PriceRecord objects, sorted by timestamp descending

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            response = self.table.query(
                KeyConditionExpression="product_id = :pid",
                ExpressionAttributeValues={":pid": self.product_id},
                Limit=limit,
                ScanIndexForward=False,  # Descending order (latest first)
            )

            records = [
                PriceRecord(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    price=float(item["price"]),
                    currency=item["currency"],
                    url=item["url"],
                    raw_text=item["raw_text"],
                )
                for item in response.get("Items", [])
            ]

            logger.info(f"Retrieved {len(records)} price records from history")
            return records

        except ClientError as e:
            logger.error(f"Failed to query price history: {e}")
            raise
