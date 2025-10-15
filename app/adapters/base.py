from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal, Protocol, TypedDict

OHLCVPoint = TypedDict(
    "OHLCVPoint",
    {
        "time": int,  # unix seconds
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": float,
    },
)


class DataAdapter(Protocol):
    source: str

    async def fetch_daily_ohlcv(self, symbol: str) -> List[OHLCVPoint]:
        ...
