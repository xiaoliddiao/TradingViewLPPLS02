### Adapters

All adapters implement `BaseAdapter.fetch_daily_ohlcv(symbol)` and return normalized daily candles.

- **Alpha Vantage**
  - Stock: `TIME_SERIES_DAILY`
  - Crypto: `DIGITAL_CURRENCY_DAILY` (USD market)
  - Notes: Free tier throttled. Requires `ALPHAVANTAGE_API_KEY` (uses `demo` if missing).

- **Stooq**
  - Endpoint: `https://stooq.com/q/d/l/?s=SYMBOL&i=d`
  - Notes: No key. Crypto sometimes available via `-usd` suffix (e.g., `btc-usd`).

- **CoinGecko**
  - Endpoint: `/coins/{id}/market_chart?vs_currency=usd&days=max&interval=daily`
  - Symbol resolution via `/coins/list`. Fallback map for popular coins.
  - No key required.

- **CoinMarketCap**
  - Endpoint: `/cryptocurrency/ohlcv/historical` (Pro API)
  - Requires `COINMARKETCAP_API_KEY`. Free tier limits apply.
