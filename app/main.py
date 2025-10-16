from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from .services import fetch_all_adapters
from .adapters import ADAPTERS
from dotenv import load_dotenv
from .lppl import fit_lppl, LPPLParams
from .datasets import list_dataset_files, read_dataset_candles_by_index, times_epoch_to_index_mapping

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


@app.post("/api/lppl")
async def post_lppl(
    symbol: str = Query("BTC"),
    source: str = Query("CoinGecko"),
    start_index: int | None = Query(None),
):
    # Fetch data from a single source for stability
    adapter = next((a for a in ADAPTERS if a.source == source), None)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Unknown source: {source}")
    data = await adapter.fetch_daily_ohlcv(symbol)
    if not data or len(data) < 60:
        raise HTTPException(status_code=400, detail="Not enough data to fit LPPL")
    import numpy as np
    times = np.array([p["time"] for p in data], dtype=float)
    closes = np.array([p["close"] for p in data], dtype=float)
    params = fit_lppl(times, closes, start_index=start_index)
    if not params:
        raise HTTPException(status_code=400, detail="LPPL fit failed")
    # Build fitted curve for overlay
    yhat = (params.A + params.B * np.clip(params.tc - times, 1e-9, None) ** params.m +
            params.C * np.clip(params.tc - times, 1e-9, None) ** params.m *
            np.cos(params.omega * np.log(np.clip(params.tc - times, 1e-9, None)) + params.phi))
    # exponentiate back to price domain
    fitted = [
        {"time": int(t), "value": float(np.exp(v))}
        for t, v in zip(times.tolist(), yhat.tolist())
    ]
    return {
        "symbol": symbol,
        "source": source,
        "params": params.__dict__,
        "fitted": fitted,
        "tc": int(params.tc),
    }


@app.get("/api/datasets")
def api_datasets():
    files = list_dataset_files()
    return {"count": len(files), "files": files}


@app.get("/api/datasets/ohlcv")
def api_dataset_ohlcv(index: int):
    path, symbol, data = read_dataset_candles_by_index(index)
    return {"index": index, "path": path, "symbol": symbol, "data": data}


@app.post("/api/datasets/lppl")
def api_dataset_lppl(index: int, start_index: int | None = None):
    import numpy as np
    path, symbol, data = read_dataset_candles_by_index(index)
    if len(data) < 60:
        raise HTTPException(status_code=400, detail="Not enough data")
    times = [p["time"] for p in data]
    closes = np.array([p["close"] for p in data], dtype=float)
    # For lppls.cmaes we feed index-based times
    t_idx, step = times_epoch_to_index_mapping(times)
    from lppls.lppls_cmaes import LPPLSCMAES
    import numpy as np
    obs = np.vstack([t_idx, closes])
    model = LPPLSCMAES(obs)
    # conservative iteration settings
    tc, m, w, a, b, c, c1, c2, O, D = model.fit(max_iteration=500, factor_sigma=0.1, pop_size=3)
    # Build fitted curve in price domain along the same index grid
    yhat = model.lppls(t_idx, tc, m, w, a, b, c1, c2)
    fitted = [{"time": int(times[i]), "value": float(yhat[i])} for i in range(len(times))]
    # Map tc from index units to epoch by linear extrapolation
    tc_epoch = int(times[0] + tc * step)
    return {
        "index": index,
        "symbol": symbol,
        "tc": tc_epoch,
        "params": {"tc": float(tc), "m": float(m), "w": float(w), "a": float(a), "b": float(b), "c": float(c), "c1": float(c1), "c2": float(c2)},
        "fitted": fitted,
    }
