from __future__ import annotations
import aiohttp
from typing import List
from .base import OHLCVPoint

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


class YahooFinanceAdapter:
    source = "Yahoo Finance"

    async def fetch_daily_ohlcv(self, symbol: str) -> List[OHLCVPoint]:
        # Yahoo Finance uses different symbols: BTC-USD, ETH-USD for crypto
        sym = symbol.upper()
        if sym in {"BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOGE", "DOT"}:
            sym = f"{sym}-USD"
        
        url = BASE_URL.format(symbol=sym)
        params = {
            "interval": "1d",
            "range": "1y",  # Last 1 year of data
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=30) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise ValueError(f"Yahoo Finance HTTP {resp.status}: {text[:200]}")
                data = await resp.json()
        
        if "chart" not in data or "result" not in data["chart"]:
            raise ValueError("Yahoo Finance: no chart data")
        
        results = data["chart"]["result"]
        if not results or not results[0]:
            raise ValueError("Yahoo Finance: empty results")
        
        result = results[0]
        timestamps = result.get("timestamp", [])
        quotes = result.get("indicators", {}).get("quote", [{}])[0]
        
        opens = quotes.get("open", [])
        highs = quotes.get("high", [])
        lows = quotes.get("low", [])
        closes = quotes.get("close", [])
        volumes = quotes.get("volume", [])
        
        points: List[OHLCVPoint] = []
        for i, ts in enumerate(timestamps):
            if i >= len(opens) or opens[i] is None or closes[i] is None:
                continue
            points.append({
                "time": int(ts),
                "open": float(opens[i]),
                "high": float(highs[i]) if highs[i] is not None else float(opens[i]),
                "low": float(lows[i]) if lows[i] is not None else float(opens[i]),
                "close": float(closes[i]),
                "volume": float(volumes[i]) if i < len(volumes) and volumes[i] is not None else 0.0,
            })
        
        return points

