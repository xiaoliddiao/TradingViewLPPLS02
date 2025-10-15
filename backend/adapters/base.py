"""
Base adapter interface for data sources.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from backend.models import OHLCVBar, AdapterResponse


class BaseAdapter(ABC):
    """Abstract base class for all data adapters."""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
    
    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, days: int = 90) -> AdapterResponse:
        """
        Fetch OHLCV data for a given symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'BTC', 'AAPL')
            days: Number of days of historical data to fetch
            
        Returns:
            AdapterResponse with data or error information
        """
        pass
    
    def _create_response(
        self, 
        symbol: str, 
        success: bool, 
        data: Optional[List[OHLCVBar]] = None, 
        error: Optional[str] = None,
        rate_limit_info: Optional[str] = None
    ) -> AdapterResponse:
        """Helper method to create standardized responses."""
        return AdapterResponse(
            adapter_name=self.name,
            symbol=symbol,
            success=success,
            data=data,
            error=error,
            rate_limit_info=rate_limit_info
        )
