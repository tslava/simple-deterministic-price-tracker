"""Data models for price tracking"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PriceRecord:
    """Represents a single price check record"""

    timestamp: datetime
    price: float
    currency: str
    url: str
    raw_text: str  # Original scraped text for debugging

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "currency": self.currency,
            "url": self.url,
            "raw_text": self.raw_text,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PriceRecord":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            price=float(data["price"]),
            currency=data["currency"],
            url=data["url"],
            raw_text=data["raw_text"],
        )
