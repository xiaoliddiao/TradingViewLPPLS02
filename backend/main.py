"""
FastAPI backend for trading data aggregator.
"""
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import asyncio

from backend.models import MultiAdapterRequest, MultiAdapterResponse, AdapterResponse
from backend.adapters import (
    AlphaVantageAdapter,
    StooqAdapter,
    CoinGeckoAdapter,
    CoinMarketCapAdapter
)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Trading Data Aggregator",
    description="Multi-source OHLCV data aggregator with TradingView charts",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize adapters
adapters = {
    "stocks": [
        AlphaVantageAdapter(api_key=os.getenv("ALPHA_VANTAGE_API_KEY")),
        StooqAdapter(),
    ],
    "crypto": [
        CoinGeckoAdapter(),
        CoinMarketCapAdapter(api_key=os.getenv("COINMARKETCAP_API_KEY")),
    ]
}


@app.get("/")
async def root():
    """Root endpoint - serve the frontend."""
    return FileResponse("frontend/index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "adapters": {
            "stocks": [adapter.name for adapter in adapters["stocks"]],
            "crypto": [adapter.name for adapter in adapters["crypto"]]
        }
    }


@app.post("/api/fetch", response_model=MultiAdapterResponse)
async def fetch_data(request: MultiAdapterRequest):
    """
    Fetch OHLCV data from all adapters simultaneously.
    
    This endpoint queries all configured data sources in parallel and returns
    the results with success/failure status for each adapter.
    """
    symbol = request.symbol
    days = request.days
    
    # Determine which adapters to use based on symbol
    # Crypto symbols are typically short (BTC, ETH, etc.)
    # Stock symbols can be longer but we'll try both types
    all_adapters = adapters["stocks"] + adapters["crypto"]
    
    # Fetch from all adapters concurrently
    tasks = [adapter.fetch_ohlcv(symbol, days) for adapter in all_adapters]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(AdapterResponse(
                adapter_name=all_adapters[i].name,
                symbol=symbol,
                success=False,
                error=f"Exception: {str(result)}"
            ))
        else:
            processed_results.append(result)
    
    return MultiAdapterResponse(
        symbol=symbol,
        results=processed_results
    )


@app.get("/api/adapters")
async def list_adapters():
    """List all available adapters with their configuration status."""
    adapter_info = []
    
    for adapter in adapters["stocks"] + adapters["crypto"]:
        info = {
            "name": adapter.name,
            "type": "stock" if adapter in adapters["stocks"] else "crypto",
            "requires_api_key": adapter.api_key is not None or adapter.name in ["Alpha Vantage", "CoinMarketCap"],
            "configured": adapter.api_key is not None and adapter.api_key != "your_alpha_vantage_key_here" and adapter.api_key != "your_coinmarketcap_key_here"
        }
        adapter_info.append(info)
    
    return {"adapters": adapter_info}


# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
