"""
Data adapters for various financial data sources.
"""
from backend.adapters.base import BaseAdapter
from backend.adapters.alpha_vantage import AlphaVantageAdapter
from backend.adapters.stooq import StooqAdapter
from backend.adapters.coingecko import CoinGeckoAdapter
from backend.adapters.coinmarketcap import CoinMarketCapAdapter

__all__ = [
    'BaseAdapter',
    'AlphaVantageAdapter',
    'StooqAdapter',
    'CoinGeckoAdapter',
    'CoinMarketCapAdapter',
]
