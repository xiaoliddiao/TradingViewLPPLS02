from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from .services import fetch_all_adapters
from .adapters import ADAPTERS
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Mini TradingView - OHLCV Aggregator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/ohlcv")
async def get_ohlcv(symbol: str = Query("BTC")):
    data, status = await fetch_all_adapters(symbol)
    return {"symbol": symbol, "data": data, "status": status}


@app.get("/api/sources")
def get_sources():
    return {"sources": [a.source for a in ADAPTERS]}


@app.get("/api/ohlcv/by-source")
async def get_ohlcv_by_source(source: str = Query(...), symbol: str = Query("BTC")):
    adapter = next((a for a in ADAPTERS if a.source == source), None)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Unknown source: {source}")
    try:
        data = await adapter.fetch_daily_ohlcv(symbol)
        return {"source": source, "symbol": symbol, "status": "ok", "data": data}
    except Exception as exc:
        return {"source": source, "symbol": symbol, "status": f"error: {exc}", "data": []}

