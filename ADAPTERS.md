### Adapters

- Alpha Vantage
  - Endpoint: `TIME_SERIES_DAILY_ADJUSTED`
  - Free tier: 25 requests/day demo key; 5 rpm; see docs `https://www.alphavantage.co/documentation/`
  - Notes: Use `apikey` env `ALPHAVANTAGE_API_KEY` (defaults to `demo`).

- Stooq
  - Endpoint: CSV daily `https://stooq.com/q/d/l/?s=<symbol>&i=d`
  - Free, no key. Symbols like `aapl`, `spy.us`, `btc-usd` may vary.
  - Notes: Lowercase symbol per Stooq convention.

- CoinGecko
  - Endpoint: `GET /api/v3/coins/{id}/ohlc?vs_currency=usd&days=365`
  - Free tier with rate limits; see docs `https://www.coingecko.com/en/api/documentation`
  - Notes: Uses internal `symbol->id` map for common coins; you can extend.

- CoinMarketCap
  - Endpoint: `GET /v1/cryptocurrency/ohlcv/historical?symbol=BTC&interval=daily`
  - Requires `COINMARKETCAP_API_KEY`; free key available with limits; docs `https://coinmarketcap.com/api/`
  - Notes: Returns quotes with volume in `quote.USD.volume`.
