from __future__ import annotations
import os
import aiohttp
from typing import List
from .base import OHLCVPoint

# CoinMarketCap free API requires API key; use /cryptocurrency/ohlcv/historical
# Docs: https://coinmarketcap.com/api/documentation/v1/#operation/getV2CryptocurrencyOhlcvHistorical
BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"

class CoinMarketCapAdapter:
    source = "CoinMarketCap"

    async def fetch_daily_ohlcv(self, symbol: str) -> List[OHLCVPoint]:
        api_key = os.getenv("COINMARKETCAP_API_KEY")
        headers = {"X-CMC_PRO_API_KEY": api_key} if api_key else {}
        params = {
            "symbol": symbol.upper(),
            "convert": "USD",
            # No time_start/time_end gives default recent range; to get max we'd paginate; keep simple
            "interval": "daily",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, params=params, headers=headers, timeout=30) as resp:
                data = await resp.json()
        quotes = (((data or {}).get("data") or {}).get("quotes")) or []
        points: List[OHLCVPoint] = []
        from datetime import datetime, timezone
        for q in quotes:
            time_open = q.get("time_open")
            if not time_open:
                continue
            # Example: 2024-01-01T00:00:00.000Z
            dt = datetime.fromisoformat(time_open.replace("Z", "+00:00")).astimezone(timezone.utc)
            quote = (q.get("quote") or {}).get("USD") or {}
            points.append({
                "time": int(dt.timestamp()),
                "open": float(quote.get("open", 0.0)),
                "high": float(quote.get("high", 0.0)),
                "low": float(quote.get("low", 0.0)),
                "close": float(quote.get("close", 0.0)),
                "volume": float(quote.get("volume", 0.0)),
            })
        return points

