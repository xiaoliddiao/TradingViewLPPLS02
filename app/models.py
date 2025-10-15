from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


ProviderName = Literal["alpha_vantage", "stooq", "coingecko", "coinmarketcap"]


class Candle(BaseModel):
    time: int = Field(..., description="Epoch seconds UTC")
    open: float
    high: float
    low: float
    close: float
    volume: float


class OHLCVResponse(BaseModel):
    provider: ProviderName
    symbol: str
    candles: List[Candle]
    error: Optional[str] = None


def utc_date_to_epoch(date_str: str) -> int:
    """Convert YYYY-MM-DD (or ISO date) to epoch seconds (UTC, midnight)."""
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return int(dt.timestamp())


def ensure_sorted(candles: List[Candle]) -> List[Candle]:
    return sorted(candles, key=lambda c: c["time"])  # ascending

