"""Configuration management with SSM Parameter Store support"""

import os
import logging
import boto3
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration"""

    PRODUCT_URL: str
    PRICE_SELECTOR: str
    DYNAMODB_TABLE: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    @classmethod
    def from_env(cls, ssm_client: Optional[boto3.client] = None) -> "Config":
        """
        Load configuration from environment variables and SSM Parameter Store

        Args:
            ssm_client: Optional boto3 SSM client (useful for testing/mocking)

        Returns:
            Config instance with loaded values

        Raises:
            ValueError: If required environment variables are missing
        """
        # Get basic config from environment variables
        product_url = os.getenv("PRODUCT_URL")
        price_selector = os.getenv("PRICE_SELECTOR")
        dynamodb_table = os.getenv("DYNAMODB_TABLE")

        if not all([product_url, price_selector, dynamodb_table]):
            raise ValueError(
                "Missing required environment variables: PRODUCT_URL, PRICE_SELECTOR, DYNAMODB_TABLE"
            )

        # Get SSM parameter names from environment
        bot_token_param = os.getenv("TELEGRAM_BOT_TOKEN_PARAM")
        chat_id_param = os.getenv("TELEGRAM_CHAT_ID_PARAM")

        if not all([bot_token_param, chat_id_param]):
            raise ValueError(
                "Missing required SSM parameter names: TELEGRAM_BOT_TOKEN_PARAM, TELEGRAM_CHAT_ID_PARAM"
            )

        # Initialize SSM client if not provided
        if ssm_client is None:
            ssm_client = boto3.client("ssm")

        # Get secrets from SSM Parameter Store
        try:
            logger.info(f"Fetching SSM parameters: {bot_token_param}, {chat_id_param}")
            response = ssm_client.get_parameters(
                Names=[bot_token_param, chat_id_param], WithDecryption=True
            )

            if len(response["Parameters"]) != 2:
                missing = set([bot_token_param, chat_id_param]) - set(
                    p["Name"] for p in response["Parameters"]
                )
                raise ValueError(f"SSM parameters not found: {missing}")

            # Create parameter name -> value mapping
            params = {p["Name"]: p["Value"] for p in response["Parameters"]}

            logger.info("Successfully loaded configuration from environment and SSM")

            return cls(
                PRODUCT_URL=product_url,
                PRICE_SELECTOR=price_selector,
                DYNAMODB_TABLE=dynamodb_table,
                TELEGRAM_BOT_TOKEN=params[bot_token_param],
                TELEGRAM_CHAT_ID=params[chat_id_param],
            )

        except Exception as e:
            logger.error(f"Failed to load SSM parameters: {e}")
            raise
