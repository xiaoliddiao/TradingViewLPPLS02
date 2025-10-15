## Changelog

### [0.2.0] - 2025-10-15 (Current)

**Major Improvements:**
- ✨ **Added Yahoo Finance adapter** as primary data source (no API key needed!)
  - Excellent coverage for both stocks (AAPL, TSLA, MSFT, SPY) and crypto (BTC, ETH, SOL)
  - Returns ~250-366 daily candles
  - Most reliable free source
- 🐛 Fixed frontend chart rendering with better error handling and console logging
- 📝 Updated CoinGecko to use 365-day limit (free tier restriction)
- 📚 Comprehensive documentation updates with adapter success rates
- 🔧 Improved error messages across all adapters
- ⚡ Better status display: shows "error: empty" vs "error: <message>"

**Technical Changes:**
- Added `app/adapters/yahoo.py` with User-Agent header for rate limit avoidance
- Enhanced frontend `index.html` with try-catch and detailed console logs
- Reordered adapters priority: Yahoo Finance → CoinGecko → others
- Removed Binance adapter (region restrictions in some locations)

### [0.1.0] - 2025-10-15 (Initial)

- 🎉 Initial release with FastAPI backend
- 📊 TradingView Lightweight Charts integration (candlestick + volume histogram)
- 🔌 Pluggable adapter architecture
- 🌐 Multi-source concurrent fetching (Alpha Vantage, Stooq, CoinGecko, CoinMarketCap)
- ✅ Real-time status badges (✓ success / ✗ error) per data source
- 🎨 Clean, modern UI with timezone selector and responsive layout
- 📖 Complete documentation (README, DECISIONS, ADAPTERS, CHANGELOG)
- 🔒 Environment variable support for API keys (.env.example)
