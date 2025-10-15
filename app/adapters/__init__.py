from .alpha_vantage import AlphaVantageAdapter
from .stooq import StooqAdapter
from .coingecko import CoinGeckoAdapter
from .coinmarketcap import CoinMarketCapAdapter
from .yahoo import YahooFinanceAdapter

ADAPTERS = [
    YahooFinanceAdapter(),
    CoinGeckoAdapter(),
    AlphaVantageAdapter(),
    StooqAdapter(),
    CoinMarketCapAdapter(),
]

