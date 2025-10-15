"""
Stooq adapter for stock data.
No API key required, free service
API Documentation: https://stooq.com/
"""
import httpx
import csv
from io import StringIO
from typing import List
from datetime import datetime, timedelta
from backend.adapters.base import BaseAdapter
from backend.models import OHLCVBar, AdapterResponse


class StooqAdapter(BaseAdapter):
    """Adapter for Stooq (stocks, no API key required)."""
    
    BASE_URL = "https://stooq.com/q/d/l/"
    
    def __init__(self):
        super().__init__("Stooq", api_key=None)
    
    async def fetch_ohlcv(self, symbol: str, days: int = 90) -> AdapterResponse:
        """Fetch stock data from Stooq."""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Stooq format: symbol in lowercase with .us suffix for US stocks
            # For common stocks, try the symbol as-is first
            params = {
                "s": symbol.lower(),
                "d1": start_date.strftime("%Y%m%d"),
                "d2": end_date.strftime("%Y%m%d"),
                "i": "d"  # daily interval
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                csv_data = response.text
            
            # Parse CSV data
            if "No data" in csv_data or len(csv_data) < 50:
                return self._create_response(
                    symbol=symbol,
                    success=False,
                    error=f"No data available for symbol '{symbol}'. Try adding .us suffix for US stocks (e.g., AAPL.US)",
                    rate_limit_info="Free service, no rate limit"
                )
            
            # Parse CSV using Python's csv module
            csv_reader = csv.DictReader(StringIO(csv_data))
            
            # Convert to OHLCV bars
            bars = []
            for row in csv_reader:
                try:
                    bars.append(OHLCVBar(
                        time=row["Date"],  # Format: YYYY-MM-DD
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=float(row["Volume"])
                    ))
                except (KeyError, ValueError) as e:
                    continue
            
            if not bars:
                return self._create_response(
                    symbol=symbol,
                    success=False,
                    error="Failed to parse data",
                    rate_limit_info="Free service, no rate limit"
                )
            
            return self._create_response(
                symbol=symbol,
                success=True,
                data=bars,
                rate_limit_info="Free service, no rate limit"
            )
            
        except httpx.HTTPError as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=f"HTTP Error: {str(e)}",
                rate_limit_info="Free service, no rate limit"
            )
        except Exception as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=f"Unexpected error: {str(e)}",
                rate_limit_info="Free service, no rate limit"
            )
