from __future__ import annotations
import asyncio
from typing import Dict, List, Tuple
from .adapters import ADAPTERS
from .adapters.base import OHLCVPoint

async def fetch_all_adapters(symbol: str) -> Tuple[Dict[str, List[OHLCVPoint]], Dict[str, str]]:
    tasks = []
    names = []
    for adapter in ADAPTERS:
        names.append(adapter.source)
        tasks.append(asyncio.create_task(_wrap_fetch(adapter, symbol)))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    data: Dict[str, List[OHLCVPoint]] = {}
    status: Dict[str, str] = {}
    for name, result in zip(names, results):
        if isinstance(result, Exception):
            status[name] = f"error: {result}"
        else:
            if result:
                data[name] = result
                status[name] = "ok"
            else:
                status[name] = "error: empty"
    return data, status

async def _wrap_fetch(adapter, symbol: str):
    return await adapter.fetch_daily_ohlcv(symbol)
