"""
Alpha Vantage adapter for stock data.
Free tier: 25 requests/day, 5 requests/minute
API Documentation: https://www.alphavantage.co/documentation/
"""
import httpx
from typing import List, Optional
from datetime import datetime
from backend.adapters.base import BaseAdapter
from backend.models import OHLCVBar, AdapterResponse


class AlphaVantageAdapter(BaseAdapter):
    """Adapter for Alpha Vantage API (stocks)."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Alpha Vantage", api_key)
    
    async def fetch_ohlcv(self, symbol: str, days: int = 90) -> AdapterResponse:
        """Fetch stock data from Alpha Vantage."""
        if not self.api_key or self.api_key == "your_alpha_vantage_key_here":
            return self._create_response(
                symbol=symbol,
                success=False,
                error="API key not configured. Get your free key at https://www.alphavantage.co/support/#api-key",
                rate_limit_info="Free tier: 25 requests/day, 5 requests/minute"
            )
        
        try:
            # Use TIME_SERIES_DAILY for stock data
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "full" if days > 100 else "compact",
                "apikey": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                return self._create_response(
                    symbol=symbol,
                    success=False,
                    error=f"API Error: {data['Error Message']}",
                    rate_limit_info="Free tier: 25 requests/day, 5 requests/minute"
                )
            
            if "Note" in data:
                return self._create_response(
                    symbol=symbol,
                    success=False,
                    error="Rate limit exceeded. Please wait a minute.",
                    rate_limit_info="Free tier: 25 requests/day, 5 requests/minute"
                )
            
            # Parse time series data
            time_series = data.get("Time Series (Daily)", {})
            if not time_series:
                return self._create_response(
                    symbol=symbol,
                    success=False,
                    error="No data available for this symbol",
                    rate_limit_info="Free tier: 25 requests/day, 5 requests/minute"
                )
            
            # Convert to OHLCV bars (sorted by date ascending)
            bars = []
            for date_str, values in sorted(time_series.items())[:days]:
                bars.append(OHLCVBar(
                    time=date_str,  # Format: YYYY-MM-DD
                    open=float(values["1. open"]),
                    high=float(values["2. high"]),
                    low=float(values["3. low"]),
                    close=float(values["4. close"]),
                    volume=float(values["5. volume"])
                ))
            
            return self._create_response(
                symbol=symbol,
                success=True,
                data=bars,
                rate_limit_info="Free tier: 25 requests/day, 5 requests/minute"
            )
            
        except httpx.HTTPError as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=f"HTTP Error: {str(e)}",
                rate_limit_info="Free tier: 25 requests/day, 5 requests/minute"
            )
        except Exception as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=f"Unexpected error: {str(e)}",
                rate_limit_info="Free tier: 25 requests/day, 5 requests/minute"
            )
