from __future__ import annotations

import os
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from app.adapters.alpha_vantage import AlphaVantageAdapter
from app.adapters.coingecko import CoinGeckoAdapter
from app.adapters.coinmarketcap import CoinMarketCapAdapter
from app.adapters.stooq import StooqAdapter
from app.models import Candle, OHLCVResponse


load_dotenv()

app = FastAPI(title="OHLCV Aggregator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


adapters = {
    "alpha_vantage": AlphaVantageAdapter(),
    "stooq": StooqAdapter(),
    "coingecko": CoinGeckoAdapter(),
    "coinmarketcap": CoinMarketCapAdapter(),
}


@app.get("/api/ohlcv/{provider}", response_model=OHLCVResponse)
async def get_ohlcv(provider: str, symbol: str = Query("BTC", min_length=1)):
    provider = provider.lower()
    if provider not in adapters:
        raise HTTPException(404, f"Unknown provider: {provider}")
    try:
        candles: List[Candle] = await adapters[provider].fetch_daily_ohlcv(symbol)
    except Exception as exc:
        return OHLCVResponse(provider=provider, symbol=symbol, candles=[], error=str(exc))
    if not candles:
        return OHLCVResponse(provider=provider, symbol=symbol, candles=[], error="no_data")
    return OHLCVResponse(provider=provider, symbol=symbol, candles=candles)


@app.get("/")
async def root():
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")
    return FileResponse(index_path)


@app.get("/static/{path:path}")
async def static_files(path: str):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", path)
    return FileResponse(file_path)

