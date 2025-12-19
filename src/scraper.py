"""Web scraping with Playwright for price extraction"""

import re
import logging
from decimal import Decimal, InvalidOperation
from typing import Tuple
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class PriceScraper:
    """Scrapes product prices from web pages using Playwright"""

    def __init__(self, url: str, selector: str, timeout: int = 30000):
        """
        Initialize scraper

        Args:
            url: Product page URL
            selector: CSS selector for price element
            timeout: Page load timeout in milliseconds (default: 30000)
        """
        self.url = url
        self.selector = selector
        self.timeout = timeout
        logger.info(f"Initialized scraper for URL: {url}")

    def scrape_price(self) -> Tuple[Decimal, str]:
        """
        Scrape price from the configured URL

        Returns:
            Tuple of (price, raw_text)

        Raises:
            PlaywrightTimeoutError: If page or element doesn't load in time
            ValueError: If price cannot be parsed
            Exception: For other scraping errors
        """
        try:
            logger.info(f"Starting price scrape from: {self.url}")

            with sync_playwright() as p:
                # Launch headless Chromium browser with Lambda-compatible settings
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--single-process',
                    ]
                )
                logger.info("Browser launched")

                try:
                    page = browser.new_page()

                    # Navigate to product page
                    logger.info(f"Navigating to {self.url}")
                    page.goto(self.url, wait_until="networkidle", timeout=self.timeout)
                    logger.info("Page loaded, waiting for price element")

                    # Wait for price element to appear (attached to DOM, doesn't need to be visible)
                    page.wait_for_selector(self.selector, state='attached', timeout=self.timeout)
                    logger.info(f"Price element found: {self.selector}")

                    # Extract price text from all matching elements, find the first visible one
                    elements = page.query_selector_all(self.selector)
                    element = None
                    for elem in elements:
                        if elem.is_visible():
                            element = elem
                            break

                    # If no visible element, use the first one
                    if not element and elements:
                        element = elements[0]
                    if not element:
                        raise ValueError(f"Element not found: {self.selector}")

                    raw_text = element.inner_text().strip()
                    logger.info(f"Raw price text extracted: '{raw_text}'")

                    # Parse price
                    price = self._parse_price(raw_text)
                    logger.info(f"Parsed price: {price}")

                    return price, raw_text

                finally:
                    browser.close()
                    logger.info("Browser closed")

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout error during scraping: {e}")
            raise

        except Exception as e:
            logger.error(f"Error during price scraping: {e}", exc_info=True)
            raise

    def _parse_price(self, text: str) -> Decimal:
        """
        Parse price from text

        Supports various formats:
        - 1,234.56
        - 1.234,56
        - 99.99
        - 151,03

        Args:
            text: Raw price text

        Returns:
            Price as Decimal

        Raises:
            ValueError: If price cannot be parsed
        """
        try:
            # Remove whitespace
            text = text.strip()
            logger.debug(f"Parsing price from: '{text}'")

            # Extract numeric part
            # Remove everything except digits, commas, and periods
            numeric_text = re.sub(r"[^\d.,]", "", text)

            if not numeric_text:
                raise ValueError(f"No numeric value found in: '{text}'")

            # Determine decimal separator
            # If both comma and period exist, the last one is the decimal separator
            has_comma = "," in numeric_text
            has_period = "." in numeric_text

            if has_comma and has_period:
                # Determine which is decimal separator based on position
                last_comma_pos = numeric_text.rfind(",")
                last_period_pos = numeric_text.rfind(".")

                if last_period_pos > last_comma_pos:
                    # Period is decimal separator (e.g., 1,234.56)
                    numeric_text = numeric_text.replace(",", "")
                else:
                    # Comma is decimal separator (e.g., 1.234,56)
                    numeric_text = numeric_text.replace(".", "").replace(",", ".")

            elif has_comma:
                # Only comma - could be thousands separator or decimal
                # If only one comma and has 2 digits after it, it's decimal
                if numeric_text.count(",") == 1:
                    parts = numeric_text.split(",")
                    if len(parts[1]) == 2:  # Decimal separator (e.g., 99,99)
                        numeric_text = numeric_text.replace(",", ".")
                    else:  # Thousands separator (e.g., 1,234)
                        numeric_text = numeric_text.replace(",", "")
                else:
                    # Multiple commas = thousands separator (e.g., 1,234,567)
                    numeric_text = numeric_text.replace(",", "")

            # Convert to Decimal
            price = Decimal(numeric_text)
            logger.debug(f"Successfully parsed: {price}")

            return price

        except (InvalidOperation, ValueError) as e:
            logger.error(f"Failed to parse price from '{text}': {e}")
            raise ValueError(f"Could not parse price from: '{text}'")
