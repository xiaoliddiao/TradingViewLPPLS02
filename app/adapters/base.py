from __future__ import annotations

import abc
from typing import List

from app.models import Candle


class BaseAdapter(abc.ABC):
    """Abstract base class for OHLCV data providers."""

    name: str

    @abc.abstractmethod
    async def fetch_daily_ohlcv(self, symbol: str) -> List[Candle]:
        """Return a list of candles with UTC epoch seconds."""
        raise NotImplementedError

