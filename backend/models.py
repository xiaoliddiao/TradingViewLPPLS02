"""
Data models for OHLCV data and API responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class OHLCVBar(BaseModel):
    """Single OHLCV bar/candle data point."""
    time: str  # ISO 8601 or unix timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float


class AdapterResponse(BaseModel):
    """Response from a data adapter."""
    adapter_name: str
    symbol: str
    success: bool
    data: Optional[List[OHLCVBar]] = None
    error: Optional[str] = None
    rate_limit_info: Optional[str] = None


class MultiAdapterRequest(BaseModel):
    """Request for fetching data from multiple adapters."""
    symbol: str = Field(default="BTC", description="Symbol to fetch (e.g., BTC, AAPL)")
    days: int = Field(default=90, ge=1, le=365, description="Number of days of historical data")


class MultiAdapterResponse(BaseModel):
    """Aggregated response from all adapters."""
    symbol: str
    results: List[AdapterResponse]
