"""
CoinGecko adapter for cryptocurrency data.
No API key required for basic usage
Free tier: 10-30 requests/minute
API Documentation: https://www.coingecko.com/en/api/documentation
"""
import httpx
from typing import List
from datetime import datetime
from backend.adapters.base import BaseAdapter
from backend.models import OHLCVBar, AdapterResponse


class CoinGeckoAdapter(BaseAdapter):
    """Adapter for CoinGecko API (crypto, no API key required)."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Common crypto symbol to CoinGecko ID mapping
    SYMBOL_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "BNB": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "USDC": "usd-coin",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "TRX": "tron",
        "AVAX": "avalanche-2",
        "SHIB": "shiba-inu",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "LTC": "litecoin",
        "UNI": "uniswap",
        "LINK": "chainlink",
        "ATOM": "cosmos",
        "XLM": "stellar",
        "XMR": "monero",
    }
    
    def __init__(self):
        super().__init__("CoinGecko", api_key=None)
    
    async def fetch_ohlcv(self, symbol: str, days: int = 90) -> AdapterResponse:
        """Fetch crypto data from CoinGecko."""
        try:
            # Convert symbol to CoinGecko ID
            symbol_upper = symbol.upper()
            coin_id = self.SYMBOL_MAP.get(symbol_upper, symbol.lower())
            
            # CoinGecko OHLC endpoint (supports up to 365 days)
            days_param = min(days, 365)
            url = f"{self.BASE_URL}/coins/{coin_id}/ohlc"
            params = {
                "vs_currency": "usd",
                "days": days_param
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            # Check for errors
            if isinstance(data, dict) and "error" in data:
                return self._create_response(
                    symbol=symbol,
                    success=False,
                    error=f"API Error: {data.get('error', 'Unknown error')}. Try symbols like BTC, ETH, SOL",
                    rate_limit_info="Free tier: 10-30 requests/minute"
                )
            
            if not data or not isinstance(data, list):
                return self._create_response(
                    symbol=symbol,
                    success=False,
                    error=f"No data available for '{symbol}'. Supported symbols: {', '.join(list(self.SYMBOL_MAP.keys())[:10])}...",
                    rate_limit_info="Free tier: 10-30 requests/minute"
                )
            
            # Convert to OHLCV bars
            # CoinGecko returns: [timestamp_ms, open, high, low, close]
            bars = []
            for item in data:
                timestamp_ms = item[0]
                date_str = datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d")
                
                bars.append(OHLCVBar(
                    time=date_str,
                    open=float(item[1]),
                    high=float(item[2]),
                    low=float(item[3]),
                    close=float(item[4]),
                    volume=0.0  # CoinGecko OHLC endpoint doesn't provide volume
                ))
            
            return self._create_response(
                symbol=symbol,
                success=True,
                data=bars,
                rate_limit_info="Free tier: 10-30 requests/minute"
            )
            
        except httpx.HTTPError as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=f"HTTP Error: {str(e)}",
                rate_limit_info="Free tier: 10-30 requests/minute"
            )
        except Exception as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=f"Unexpected error: {str(e)}",
                rate_limit_info="Free tier: 10-30 requests/minute"
            )
