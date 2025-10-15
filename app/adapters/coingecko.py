from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp

from app.adapters.base import BaseAdapter
from app.models import Candle


class CoinGeckoAdapter(BaseAdapter):
    name = "coingecko"
    BASE_URL = "https://api.coingecko.com/api/v3"
    def __init__(self, api_key: Optional[str] = None) -> None:
        # CoinGecko increasingly requires an API key even for free tier
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY")

    async def _get(self, session: aiohttp.ClientSession, path: str, params: Optional[dict] = None):
        headers = {
            "accept": "application/json",
            "user-agent": "ohlcv-aggregator/0.1 (+https://example.com)",
        }
        if self.api_key:
            # CoinGecko expects x-cg-pro-api-key header
            headers["x-cg-pro-api-key"] = self.api_key
        async with session.get(
            f"{self.BASE_URL}{path}", params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _symbol_to_id(self, session: aiohttp.ClientSession, symbol: str) -> Optional[str]:
        # Try direct coin list map (cached on CG side). This list can be large.
        try:
            coins = await self._get(session, "/coins/list")
        except Exception:
            return None
        symbol_upper = symbol.upper()
        for c in coins:
            if c.get("symbol", "").upper() == symbol_upper:
                return c.get("id")
        return None

    async def fetch_daily_ohlcv(self, symbol: str) -> List[Candle]:
        async with aiohttp.ClientSession() as session:
            # Prefer well-known mappings first to avoid ambiguous symbol matches
            preferred: Dict[str, str] = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "BNB": "binancecoin",
                "USDT": "tether",
                "USDC": "usd-coin",
            }
            coin_id = preferred.get(symbol.upper())
            if not coin_id:
                coin_id = await self._symbol_to_id(session, symbol)
            if not coin_id:
                # Still couldn't resolve
                fallback: Dict[str, str] = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "BNB": "binancecoin"}
                coin_id = fallback.get(symbol.upper())
            if not coin_id:
                return []
            # Prefer a 1-year window to reduce payload and avoid anonymous limits
            for days in ("365", "180", "90", "30"):
                try:
                    data = await self._get(
                        session,
                        f"/coins/{coin_id}/market_chart",
                        params={"vs_currency": "usd", "days": days, "interval": "daily"},
                    )
                    break
                except Exception:
                    data = None
            if not data:
                return []
            prices = data.get("prices") or []
            volumes = data.get("total_volumes") or []
            # CoinGecko returns [ms, price] points; for OHLC we can approximate with daily sampled close/open/high/low using prices bucketed per day
            # We'll group by date (UTC) and compute OHLC from intraday prices.
            daily_map: Dict[str, List[float]] = {}
            for ts_ms, price in prices:
                dt = datetime.utcfromtimestamp(ts_ms / 1000)
                date_key = dt.strftime("%Y-%m-%d")
                daily_map.setdefault(date_key, []).append(float(price))
            vol_map: Dict[str, float] = {}
            for ts_ms, vol in volumes:
                dt = datetime.utcfromtimestamp(ts_ms / 1000)
                date_key = dt.strftime("%Y-%m-%d")
                vol_map[date_key] = float(vol)
            candles: List[Candle] = []
            for date_key, prices_list in daily_map.items():
                if not prices_list:
                    continue
                dt = datetime.fromisoformat(date_key)
                open_p = prices_list[0]
                close_p = prices_list[-1]
                high_p = max(prices_list)
                low_p = min(prices_list)
                volume = vol_map.get(date_key, 0.0)
                candles.append(
                    {
                        "time": int(dt.timestamp()),
                        "open": open_p,
                        "high": high_p,
                        "low": low_p,
                        "close": close_p,
                        "volume": volume,
                    }
                )
            candles.sort(key=lambda c: c["time"])  # ascending
            return candles

