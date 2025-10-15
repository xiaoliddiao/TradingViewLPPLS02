from .alpha_vantage import AlphaVantageAdapter
from .stooq import StooqAdapter
from .coingecko import CoinGeckoAdapter
from .coinmarketcap import CoinMarketCapAdapter

ADAPTERS = [
    AlphaVantageAdapter(),
    StooqAdapter(),
    CoinGeckoAdapter(),
    CoinMarketCapAdapter(),
]
