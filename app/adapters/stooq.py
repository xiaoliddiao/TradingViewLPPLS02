from __future__ import annotations
import aiohttp
from typing import List
from .base import OHLCVPoint

# Stooq provides CSV daily data via http://stooq.com/q/d/l/?s=aapl&i=d
BASE_URL = "https://stooq.com/q/d/l/"

class StooqAdapter:
    source = "Stooq"

    async def fetch_daily_ohlcv(self, symbol: str) -> List[OHLCVPoint]:
        # Try a few common symbol variants
        sym = symbol.lower()
        candidates = [sym]
        # US stocks commonly use .us on Stooq
        if not sym.endswith('.us'):
            candidates.append(f"{sym}.us")
        # Crypto pairs often use -usd
        if "-" not in sym:
            candidates.append(f"{sym}-usd")

        text = ""
        async with aiohttp.ClientSession() as session:
            for cand in candidates:
                params = {"s": cand, "i": "d"}
                async with session.get(BASE_URL, params=params, timeout=30) as resp:
                    t = await resp.text()
                # Heuristic: CSV header starts with 'Date,Open,High,Low,Close,Volume' and has > 1 line
                if t.lower().startswith("date,open,high,low,close") and t.count("\n") > 1:
                    text = t
                    break
        if not text:
            return []
        # Parse CSV: date,open,high,low,close,volume
        import csv
        from io import StringIO
        from datetime import datetime, timezone
        points: List[OHLCVPoint] = []
        reader = csv.DictReader(StringIO(text))
        for row in reader:
            if not row.get("date"):
                continue
            dt = datetime.strptime(row["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            points.append({
                "time": int(dt.timestamp()),
                "open": float(row["open"] or 0.0),
                "high": float(row["high"] or 0.0),
                "low": float(row["low"] or 0.0),
                "close": float(row["close"] or 0.0),
                "volume": float(row.get("volume") or 0.0),
            })
        return points
