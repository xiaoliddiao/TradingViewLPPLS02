### Key Design Decisions

- **FastAPI + aiohttp**: Async-first to concurrently fetch from providers when needed and keep the server simple.
- **Pluggable adapters**: Each provider implements `BaseAdapter.fetch_daily_ohlcv(symbol)` returning normalized candles. This enables swapping or extending providers.
- **Daily frequency**: All providers normalized to daily candles for consistency with free endpoints and fair quotas.
- **Pydantic models**: Response schema stability and FastAPI integration; `Candle` and `OHLCVResponse` ensure typed output.
- **Frontend SPA**: Plain JS + TradingView Lightweight Charts via CDN for minimal setup and strong UX (zoom/pan/crosshair/resize built-in).
- **Symbol handling**: Crypto defaults to USD where needed; Stooq tries `symbol` and `symbol-usd`. CoinGecko resolves `symbol -> id` via `/coins/list` and a small fallback map.
- **API keys**: `.env`-based. Alpha Vantage supports a `demo` key for limited testing; CoinMarketCap requires user key to enable the adapter.

### Provider Notes (as of 2025-10)
- Alpha Vantage: `TIME_SERIES_DAILY` (stocks), `DIGITAL_CURRENCY_DAILY` (crypto). Free tier throttled.
- Stooq: CSV endpoint `https://stooq.com/q/d/l/?s=SYMBOL&i=d` with no key.
- CoinGecko: `/coins/{id}/market_chart?vs_currency=usd&days=max&interval=daily`.
- CoinMarketCap: `/cryptocurrency/ohlcv/historical` requires key.

### Error Handling
- If a provider returns no data or errors, the API returns `error` with `no_data` or message; frontend shows ❌ for that provider.

### Alternatives Considered
- Server-side aggregation across providers in a single call was deferred to keep per-provider visibility and status UX.
- Redis caching could reduce API usage but is out-of-scope for the starter.
