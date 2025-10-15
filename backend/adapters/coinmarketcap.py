"""
CoinMarketCap adapter for cryptocurrency data.
Requires API key (free tier: 10,000 credits/month)
API Documentation: https://coinmarketcap.com/api/documentation/v1/
"""
import httpx
from typing import List
from datetime import datetime, timedelta
from backend.adapters.base import BaseAdapter
from backend.models import OHLCVBar, AdapterResponse


class CoinMarketCapAdapter(BaseAdapter):
    """Adapter for CoinMarketCap API (crypto)."""
    
    BASE_URL = "https://pro-api.coinmarketcap.com/v1"
    SANDBOX_URL = "https://sandbox-api.coinmarketcap.com/v1"
    
    def __init__(self, api_key: str = None):
        super().__init__("CoinMarketCap", api_key)
    
    async def fetch_ohlcv(self, symbol: str, days: int = 90) -> AdapterResponse:
        """Fetch crypto data from CoinMarketCap."""
        if not self.api_key or self.api_key == "your_coinmarketcap_key_here":
            return self._create_response(
                symbol=symbol,
                success=False,
                error="API key not configured. Get your free key at https://coinmarketcap.com/api/",
                rate_limit_info="Free tier: 10,000 credits/month"
            )
        
        try:
            # First, get the cryptocurrency ID
            headers = {
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accept": "application/json"
            }
            
            # Get crypto ID from symbol
            map_url = f"{self.BASE_URL}/cryptocurrency/map"
            params = {"symbol": symbol.upper()}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get cryptocurrency ID
                response = await client.get(map_url, headers=headers, params=params)
                response.raise_for_status()
                map_data = response.json()
                
                if map_data.get("status", {}).get("error_code") != 0:
                    error_msg = map_data.get("status", {}).get("error_message", "Unknown error")
                    return self._create_response(
                        symbol=symbol,
                        success=False,
                        error=f"API Error: {error_msg}",
                        rate_limit_info="Free tier: 10,000 credits/month"
                    )
                
                crypto_data = map_data.get("data", [])
                if not crypto_data:
                    return self._create_response(
                        symbol=symbol,
                        success=False,
                        error=f"Symbol '{symbol}' not found. Try BTC, ETH, etc.",
                        rate_limit_info="Free tier: 10,000 credits/month"
                    )
                
                crypto_id = crypto_data[0]["id"]
                
                # Get OHLCV data (Note: Historical OHLCV requires paid plan)
                # Using quotes/latest as fallback for free tier
                quotes_url = f"{self.BASE_URL}/cryptocurrency/quotes/latest"
                quote_params = {"id": crypto_id, "convert": "USD"}
                
                response = await client.get(quotes_url, headers=headers, params=quote_params)
                response.raise_for_status()
                quotes_data = response.json()
                
                if quotes_data.get("status", {}).get("error_code") != 0:
                    error_msg = quotes_data.get("status", {}).get("error_message", "Unknown error")
                    return self._create_response(
                        symbol=symbol,
                        success=False,
                        error=f"API Error: {error_msg}",
                        rate_limit_info="Free tier: 10,000 credits/month"
                    )
                
                # Note: Free tier only provides current price, not historical OHLCV
                # Creating a single bar with current data
                crypto_quote = quotes_data.get("data", {}).get(str(crypto_id), {})
                if not crypto_quote:
                    return self._create_response(
                        symbol=symbol,
                        success=False,
                        error="No quote data available",
                        rate_limit_info="Free tier: 10,000 credits/month (Historical OHLCV requires paid plan)"
                    )
                
                quote = crypto_quote.get("quote", {}).get("USD", {})
                current_price = quote.get("price", 0)
                volume_24h = quote.get("volume_24h", 0)
                percent_change_24h = quote.get("percent_change_24h", 0)
                
                # Create a single bar with current data
                # Note: This is a limitation of the free tier
                bars = [
                    OHLCVBar(
                        time=datetime.now().strftime("%Y-%m-%d"),
                        open=current_price * (1 - percent_change_24h / 100),
                        high=current_price * 1.01,  # Approximation
                        low=current_price * 0.99,   # Approximation
                        close=current_price,
                        volume=volume_24h
                    )
                ]
                
                return self._create_response(
                    symbol=symbol,
                    success=True,
                    data=bars,
                    rate_limit_info="Free tier: 10,000 credits/month (Historical OHLCV requires paid plan - showing current data only)"
                )
            
        except httpx.HTTPError as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=f"HTTP Error: {str(e)}",
                rate_limit_info="Free tier: 10,000 credits/month"
            )
        except Exception as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=f"Unexpected error: {str(e)}",
                rate_limit_info="Free tier: 10,000 credits/month"
            )
