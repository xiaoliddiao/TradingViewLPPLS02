from __future__ import annotations
import os
import aiohttp
from typing import List
from .base import OHLCVPoint

API_URL = "https://www.alphavantage.co/query"

CRYPTO_SYMBOLS = {"BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "TRX"}


class AlphaVantageAdapter:
    source = "Alpha Vantage"

    async def fetch_daily_ohlcv(self, symbol: str) -> List[OHLCVPoint]:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY", "demo")
        symbol_up = symbol.upper()
        is_crypto = symbol_up in CRYPTO_SYMBOLS
        if is_crypto:
            params = {
                "function": "DIGITAL_CURRENCY_DAILY",
                "symbol": symbol_up,
                "market": "USD",
                "apikey": api_key,
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, params=params, timeout=30) as resp:
                    data = await resp.json()
            series = data.get("Time Series (Digital Currency Daily)") or {}
            points: List[OHLCVPoint] = []
            from datetime import datetime, timezone
            for day, values in sorted(series.items()):
                open_ = float(values.get("1b. open (USD)") or values.get("1a. open (USD)") or values.get("1. open", 0.0))
                high = float(values.get("2b. high (USD)") or values.get("2. high", 0.0))
                low = float(values.get("3b. low (USD)") or values.get("3. low", 0.0))
                close = float(values.get("4b. close (USD)") or values.get("4. close", 0.0))
                volume = float(values.get("5. volume", 0.0))
                dt = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                points.append({
                    "time": int(dt.timestamp()),
                    "open": open_,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": volume,
                })
            return points
        else:
            params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": symbol_up,
                "apikey": api_key,
                "outputsize": "compact",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, params=params, timeout=30) as resp:
                    data = await resp.json()
            series = data.get("Time Series (Daily)") or {}
            points = []
            from datetime import datetime, timezone
            for day, values in sorted(series.items()):
                open_ = float(values.get("1. open", 0.0))
                high = float(values.get("2. high", 0.0))
                low = float(values.get("3. low", 0.0))
                close = float(values.get("4. close", 0.0))
                volume = float(values.get("6. volume", values.get("5. volume", 0.0)))
                dt = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                points.append({
                    "time": int(dt.timestamp()),
                    "open": open_,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": volume,
                })
            return points
