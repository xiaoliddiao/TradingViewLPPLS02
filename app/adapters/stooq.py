from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO
from typing import List

import aiohttp

from app.adapters.base import BaseAdapter
from app.models import Candle


class StooqAdapter(BaseAdapter):
    name = "stooq"
    BASE_URL = "https://stooq.com/q/d/l/"

    async def fetch_daily_ohlcv(self, symbol: str) -> List[Candle]:
        # Stooq symbols often require suffixes; try several common variations
        s = symbol.lower()
        candidates = [
            s,
            f"{s}-usd",
            f"{s}_usd",
            f"{s}.us",
        ]
        params_common = {"i": "d"}
        async with aiohttp.ClientSession() as session:
            for sym in candidates:
                params = {"s": sym, **params_common}
                try:
                    async with session.get(self.BASE_URL, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        if resp.status != 200:
                            continue
                        text = await resp.text()
                except Exception:
                    continue
                if not text or text.startswith("<!DOCTYPE html"):
                    continue
                candles: List[Candle] = []
                reader = csv.DictReader(StringIO(text))
                # Expected headers: Date,Open,High,Low,Close,Volume
                for row in reader:
                    if not row.get("Date"):
                        continue
                    dt = datetime.fromisoformat(row["Date"])  # YYYY-MM-DD
                    try:
                        candles.append(
                            {
                                "time": int(dt.timestamp()),
                                "open": float(row["Open"]),
                                "high": float(row["High"]),
                                "low": float(row["Low"]),
                                "close": float(row["Close"]),
                                "volume": float(row.get("Volume") or 0),
                            }
                        )
                    except Exception:
                        continue
                if candles:
                    candles.sort(key=lambda c: c["time"])  # ascending
                    return candles
        return []

