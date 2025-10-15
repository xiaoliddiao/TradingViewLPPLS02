### Adapters

Each adapter is implemented in `app/adapters/`. Here's a summary of all data sources:

#### Yahoo Finance (PRIMARY - Best Coverage!)
- **Endpoint**: `GET https://query1.finance.yahoo.com/v8/finance/chart/{symbol}`
- **Auth**: None required - completely free public API
- **Coverage**: 
  - Stocks: AAPL, TSLA, MSFT, SPY, etc.
  - Crypto: Auto-converts BTC→BTC-USD, ETH→ETH-USD
- **Notes**: 
  - Returns ~366 days of daily data
  - Most reliable source for both stocks and crypto
  - Add User-Agent header to avoid rate limits
- **Success Rate**: ✓ Excellent

#### CoinGecko
- **Endpoint**: `GET /api/v3/coins/{id}/ohlc?vs_currency=usd&days=365`
- **Auth**: None required (free tier has rate limits)
- **Coverage**: Crypto only (BTC, ETH, SOL, etc.)
- **Docs**: https://www.coingecko.com/en/api/documentation
- **Notes**: 
  - Uses internal symbol→id mapping (bitcoin, ethereum, solana)
  - Free tier limited to last 365 days
  - Returns ~92 data points (daily candles)
- **Success Rate**: ✓ Good for crypto

#### Alpha Vantage
- **Endpoint**: `GET https://www.alphavantage.co/query`
- **Auth**: API key required (set `ALPHAVANTAGE_API_KEY` in `.env`)
- **Free Tier**: 
  - Demo key: 25 requests/day
  - Free key: 500 requests/day
- **Coverage**: 
  - Stocks: TIME_SERIES_DAILY_ADJUSTED
  - Crypto: DIGITAL_CURRENCY_DAILY
- **Docs**: https://www.alphavantage.co/documentation/
- **Notes**: Without proper key, returns empty or limited data
- **Success Rate**: ⚠ Requires valid API key

#### Stooq
- **Endpoint**: `GET https://stooq.com/q/d/l/?s={symbol}&i=d`
- **Auth**: None required - free CSV endpoint
- **Coverage**: Stocks (limited)
- **Notes**: 
  - US stocks use `.us` suffix (e.g., `aapl.us`)
  - Crypto uses `-usd` suffix (e.g., `btc-usd`)
  - Symbol variations make it unreliable
- **Success Rate**: ⚠ Limited

#### CoinMarketCap
- **Endpoint**: `GET https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical`
- **Auth**: API key required (set `COINMARKETCAP_API_KEY` in `.env`)
- **Free Tier**: 333 credits/day, 10k credits/month
- **Coverage**: Crypto only
- **Docs**: https://coinmarketcap.com/api/documentation/v1/
- **Notes**: Returns empty without valid API key
- **Success Rate**: ⚠ Requires valid API key

---

### Recommended Setup

For best results without API keys:
1. **Yahoo Finance** - handles both stocks and crypto automatically
2. **CoinGecko** - backup for crypto data

For production with API keys:
1. Set `ALPHAVANTAGE_API_KEY` in `.env` for extended stock coverage
2. Set `COINMARKETCAP_API_KEY` in `.env` for additional crypto data
