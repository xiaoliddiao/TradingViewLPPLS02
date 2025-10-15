### OHLCV Aggregator with TradingView Lightweight Charts

Production-ready starter that fetches daily OHLCV from multiple free/cheap providers and renders candlestick charts with TradingView Lightweight Charts.

Providers:
- Alpha Vantage (stocks + some crypto)
- Stooq (stocks, some crypto via `-usd` suffix)
- CoinGecko (crypto)
- CoinMarketCap (crypto, requires API key)

### Quickstart (macOS, with Python virtualenv)

1) Install Python 3.11 (recommended) and pipx/pip. On macOS:
```bash
brew install python@3.11
```

2) Clone and setup virtualenv:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Configure environment:
```bash
cp .env.example .env
# Edit .env to set ALPHAVANTAGE_API_KEY and COINMARKETCAP_API_KEY (optional)
```

4) Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

5) Open the UI:
`http://localhost:8000/`

Type a symbol like `BTC` (for crypto) or `AAPL` (for stocks). The page fetches data from all providers in parallel. A checkmark means data loaded; a cross means provider failed for the given symbol or rate-limited.

### Notes on free endpoints and quotas (2025-10)
- Alpha Vantage: Free API with 25 req/day on free tier, 5 req/min. Endpoints used: `TIME_SERIES_DAILY` (stocks), `DIGITAL_CURRENCY_DAILY` (crypto). Requires API key; demo key is limited.
- Stooq: Public CSV downloads for many tickers, daily frequency. No key.
- CoinGecko: Free API, generous but rate-limited. Using `/coins/{id}/market_chart?days=max&interval=daily`.
- CoinMarketCap: Pro API requires key; free tier limited. Using `/cryptocurrency/ohlcv/historical`.

If a provider does not support a symbol or rate-limits, it will show a cross.

### Development
Run formatting/lints as you prefer. The code is modular: adapters live in `app/adapters`, response models in `app/models.py`, and the SPA in `static/`.

