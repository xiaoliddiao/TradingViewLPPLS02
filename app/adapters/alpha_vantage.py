from __future__ import annotations

import os
from datetime import datetime
from typing import List

import aiohttp

from app.adapters.base import BaseAdapter
from app.models import Candle


class AlphaVantageAdapter(BaseAdapter):
    name = "alpha_vantage"

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY", "demo")

    async def _fetch(self, session: aiohttp.ClientSession, params: dict) -> dict:
        async with session.get(self.BASE_URL, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            resp.raise_for_status()
            return await resp.json()

    @staticmethod
    def _parse_time_series_daily(data: dict) -> List[Candle]:
        ts = data.get("Time Series (Daily)") or data.get("Time Series (Digital Currency Daily)")
        if not ts:
            return []
        candles: List[Candle] = []
        for date_str, values in ts.items():
            # Alpha Vantage keys vary between stock and crypto endpoints
            open_val = values.get("1. open") or values.get("1a. open (USD)") or values.get("1b. open (USD)")
            high_val = values.get("2. high") or values.get("2a. high (USD)")
            low_val = values.get("3. low") or values.get("3a. low (USD)")
            close_val = values.get("4. close") or values.get("4a. close (USD)")
            volume_val = values.get("5. volume") or values.get("5. volume") or values.get("5. volume")
            dt = datetime.fromisoformat(date_str)
            candles.append(
                {
                    "time": int(dt.timestamp()),
                    "open": float(open_val),
                    "high": float(high_val),
                    "low": float(low_val),
                    "close": float(close_val),
                    "volume": float(volume_val or 0),
                }
            )
        candles.sort(key=lambda c: c["time"])  # ascending
        return candles

    async def fetch_daily_ohlcv(self, symbol: str) -> List[Candle]:
        # Try stocks first using TIME_SERIES_DAILY, then crypto as DIGI endpoint if looks like crypto
        params_stock = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact",
        }

        params_crypto = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": "USD",
            "apikey": self.api_key,
        }

        async with aiohttp.ClientSession() as session:
            # Prefer crypto if symbol is common like BTC or ETH
            preferred_order = [params_crypto, params_stock] if symbol.upper() in {"BTC", "ETH", "SOL", "BNB"} else [params_stock, params_crypto]
            for params in preferred_order:
                try:
                    data = await self._fetch(session, params)
                except Exception:
                    continue
                candles = self._parse_time_series_daily(data)
                if candles:
                    return candles
        return []

