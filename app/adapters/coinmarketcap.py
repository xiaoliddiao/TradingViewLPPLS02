from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

import aiohttp

from app.adapters.base import BaseAdapter
from app.models import Candle


class CoinMarketCapAdapter(BaseAdapter):
    name = "coinmarketcap"
    BASE_URL = "https://pro-api.coinmarketcap.com/v1"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("COINMARKETCAP_API_KEY")

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            return {}
        return {"X-CMC_PRO_API_KEY": self.api_key}

    async def _get(self, session: aiohttp.ClientSession, path: str, params: Optional[dict] = None):
        async with session.get(
            f"{self.BASE_URL}{path}", params=params, headers=self._headers(), timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _symbol_to_id(self, session: aiohttp.ClientSession, symbol: str) -> Optional[int]:
        try:
            data = await self._get(session, "/cryptocurrency/map", params={"symbol": symbol})
        except Exception:
            return None
        for item in data.get("data", []) or []:
            if item.get("symbol", "").upper() == symbol.upper():
                return int(item.get("id"))
        return None

    async def fetch_daily_ohlcv(self, symbol: str) -> List[Candle]:
        if not self.api_key:
            # Without API key, skip to avoid 401
            return []
        async with aiohttp.ClientSession() as session:
            cmc_id = await self._symbol_to_id(session, symbol)
            if not cmc_id:
                return []
            # Use historical OHLCV daily endpoint
            try:
                data = await self._get(
                    session,
                    f"/cryptocurrency/ohlcv/historical",
                    params={"id": cmc_id, "convert": "USD"},
                )
            except Exception:
                return []
            quotes = (data.get("data") or {}).get("quotes") or []
            candles: List[Candle] = []
            for q in quotes:
                t_str = ((q.get("time_open") or q.get("timestamp")) or "").replace("Z", "+00:00")
                try:
                    dt = datetime.fromisoformat(t_str)
                except Exception:
                    try:
                        dt = datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%S%z")
                    except Exception:
                        continue
                o = q["quote"]["USD"]["open"]
                h = q["quote"]["USD"]["high"]
                l = q["quote"]["USD"]["low"]
                c = q["quote"]["USD"]["close"]
                v = q["quote"]["USD"].get("volume") or 0
                candles.append(
                    {
                        "time": int(dt.astimezone(timezone.utc).timestamp()),
                        "open": float(o),
                        "high": float(h),
                        "low": float(l),
                        "close": float(c),
                        "volume": float(v),
                    }
                )
            candles.sort(key=lambda c: c["time"])  # ascending
            return candles

