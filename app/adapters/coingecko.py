from __future__ import annotations
import aiohttp
from typing import List
from .base import OHLCVPoint

# CoinGecko free v3: /coins/{id}/ohlc?vs_currency=usd&days=max
# For BTC id is 'bitcoin'
BASE_URL = "https://api.coingecko.com/api/v3/coins/{id}/ohlc"

COINGECKO_SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
}

class CoinGeckoAdapter:
    source = "CoinGecko"

    def _symbol_to_id(self, symbol: str) -> str:
        return COINGECKO_SYMBOL_TO_ID.get(symbol.upper(), symbol.lower())

    async def fetch_daily_ohlcv(self, symbol: str) -> List[OHLCVPoint]:
        coin_id = self._symbol_to_id(symbol)
        url = BASE_URL.format(id=coin_id)
        # Public API (no key) allows up to last 365 days on OHLC
        params = {"vs_currency": "usd", "days": "365"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=30) as resp:
                # CoinGecko sometimes returns error json or text; try json then fallback
                try:
                    data = await resp.json(content_type=None)
                except Exception:
                    text = await resp.text()
                    raise ValueError(f"unexpected response: {text[:200]}")
        # data is list of [timestamp(ms), open, high, low, close]
        if isinstance(data, dict):
            # Error payloads look like {"status":{"error_code":..., "error_message":...}} or {"error":"..."}
            err = data.get("error") or data.get("status") or data
            raise ValueError(f"CoinGecko error: {err}")
        if not isinstance(data, list):
            raise ValueError("CoinGecko unexpected data shape")

        points: List[OHLCVPoint] = []
        for entry in data:
            if not isinstance(entry, (list, tuple)) or len(entry) < 5:
                continue
            ts_ms, o, h, l, c = entry[:5]
            ts_ms_int = int(float(ts_ms))
            # CoinGecko OHLC has no volume in this endpoint; leave 0
            points.append({
                "time": ts_ms_int // 1000,
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": 0.0,
            })
        return points
