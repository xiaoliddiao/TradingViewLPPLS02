### Mini TradingView - OHLCV Aggregator

A small, production-ready starter that fetches daily OHLCV from multiple free/cheap sources and renders charts with TradingView Lightweight Charts.

Adapters:
- Alpha Vantage (stocks)
- Stooq (stocks)
- CoinGecko (crypto)
- CoinMarketCap (crypto)

#### Quickstart (macOS + Python venv)

```bash
# 1) Clone and enter
git clone <your-repo-url>
cd <repo>

# 2) Python 3.11 recommended
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3) Environment (optional keys)
cp .env.example .env
# Edit .env to add ALPHAVANTAGE_API_KEY and COINMARKETCAP_API_KEY if you have them

# 4) Run
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5) Open UI
open http://localhost:8000/static/index.html
```

#### Environment

Create `.env` with optional keys:

```bash
ALPHAVANTAGE_API_KEY=demo
COINMARKETCAP_API_KEY=
```

If keys are missing, those adapters may error or return limited data.

#### API

- `GET /api/ohlcv?symbol=BTC` – concurrently fetches from all adapters, returns per-source data and status. The UI shows a ✓ for success or ✗ for failure. The first successful dataset is rendered immediately.

See `ADAPTERS.md` and `DECISIONS.md` for design/details.
