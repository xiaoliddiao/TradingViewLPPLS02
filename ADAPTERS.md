# Data Adapters Documentation

This document provides detailed information about each data adapter, including setup, configuration, limitations, and troubleshooting.

## Table of Contents

1. [Overview](#overview)
2. [Alpha Vantage](#alpha-vantage)
3. [Stooq](#stooq)
4. [CoinGecko](#coingecko)
5. [CoinMarketCap](#coinmarketcap)
6. [Adding Custom Adapters](#adding-custom-adapters)

---

## Overview

All adapters implement the `BaseAdapter` interface, which ensures consistent behavior:

```python
class BaseAdapter(ABC):
    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, days: int = 90) -> AdapterResponse
```

### Response Format

Each adapter returns an `AdapterResponse` with:

- `adapter_name`: Name of the adapter
- `symbol`: Requested symbol
- `success`: Boolean indicating success/failure
- `data`: List of OHLCV bars (if successful)
- `error`: Error message (if failed)
- `rate_limit_info`: Information about API rate limits

---

## Alpha Vantage

### Description

Alpha Vantage provides stock market data, forex, and cryptocurrency information.

**Type**: Stock Market Data  
**Authentication**: API Key Required  
**Cost**: Free tier available

### Setup

1. **Get API Key**:
   - Visit: https://www.alphavantage.co/support/#api-key
   - Fill out the form (name, email, organization)
   - Receive key instantly via email

2. **Configure**:
   ```bash
   # In .env file
   ALPHA_VANTAGE_API_KEY=your_actual_key_here
   ```

### Rate Limits

**Free Tier**:
- 25 API requests per day
- 5 API requests per minute
- No credit card required

**Premium Tiers** (optional):
- 30 requests/minute: $49.99/month
- 75 requests/minute: $149.99/month
- 300 requests/minute: $499.99/month

### Supported Symbols

**U.S. Stocks**: AAPL, MSFT, GOOGL, TSLA, AMZN, etc.  
**International Stocks**: Use exchange suffix (e.g., VOD.LON, TCS.BSE)  
**ETFs**: SPY, QQQ, VTI, etc.  
**Forex**: Use pairs like EUR/USD  
**Crypto**: BTC, ETH (via DIGITAL_CURRENCY functions)

### Features

- Daily, weekly, monthly time series
- Intraday data (1min, 5min, 15min, 30min, 60min)
- Adjusted for splits and dividends
- Full or compact output size

### Data Quality

✅ **Pros**:
- High-quality, reliable data
- Long history available
- Good documentation
- Includes volume data

❌ **Cons**:
- Very limited free tier
- Rate limiting can be restrictive
- Requires API key setup

### Example Usage

```python
adapter = AlphaVantageAdapter(api_key="your_key")
result = await adapter.fetch_ohlcv("AAPL", days=90)
```

### Troubleshooting

**Error: "API key not configured"**
- Solution: Add key to `.env` file

**Error: "Rate limit exceeded"**
- Solution: Wait 1 minute, or upgrade to premium
- Check remaining quota at API status page

**Error: "Invalid API call"**
- Solution: Check symbol format
- U.S. stocks don't need suffix
- International stocks need exchange suffix

**No data returned**
- Check if market is open (stocks only trade during market hours)
- Verify symbol exists and is spelled correctly
- Try using full output size

### Implementation Details

**File**: `backend/adapters/alpha_vantage.py`

**API Endpoint**: `https://www.alphavantage.co/query`

**Function Used**: `TIME_SERIES_DAILY`

**Parameters**:
- `function`: TIME_SERIES_DAILY
- `symbol`: Stock ticker
- `outputsize`: full (all data) or compact (last 100 days)
- `apikey`: Your API key

**Response Parsing**:
```python
time_series = data["Time Series (Daily)"]
for date, values in time_series.items():
    open = values["1. open"]
    high = values["2. high"]
    low = values["3. low"]
    close = values["4. close"]
    volume = values["5. volume"]
```

---

## Stooq

### Description

Stooq provides free historical stock market data without requiring API keys.

**Type**: Stock Market Data  
**Authentication**: None Required  
**Cost**: Free

### Setup

No setup required! Works out of the box.

### Rate Limits

**Free Service**:
- No official rate limits
- Fair use policy applies
- Don't abuse the service

### Supported Symbols

**U.S. Stocks**: AAPL.US, MSFT.US, GOOGL.US (note the .US suffix)  
**Polish Stocks**: PKO, PZU, KGHM  
**Indices**: ^SPX (S&P 500), ^DJI (Dow Jones)

### Symbol Format

**Important**: Most symbols require a suffix:
- U.S. stocks: `SYMBOL.US` (e.g., AAPL.US)
- U.K. stocks: `SYMBOL.UK`
- German stocks: `SYMBOL.DE`

### Features

- Daily historical data
- CSV format (simple parsing)
- No authentication
- Quick response times

### Data Quality

✅ **Pros**:
- No API key needed
- No rate limits
- Simple CSV format
- Free forever

❌ **Cons**:
- Symbol format can be confusing
- Less comprehensive than paid services
- No official API documentation
- Limited to daily data

### Example Usage

```python
adapter = StooqAdapter()
result = await adapter.fetch_ohlcv("AAPL.US", days=90)
```

### Troubleshooting

**Error: "No data available"**
- Solution: Add appropriate suffix (.US, .UK, etc.)
- Example: Change "AAPL" to "AAPL.US"

**Error: "Failed to parse data"**
- Solution: Check CSV format hasn't changed
- Verify symbol exists on Stooq

**Partial data returned**
- Some symbols have limited history
- Newly listed stocks may have less data

### Implementation Details

**File**: `backend/adapters/stooq.py`

**API Endpoint**: `https://stooq.com/q/d/l/`

**Parameters**:
- `s`: Symbol (lowercase with suffix)
- `d1`: Start date (YYYYMMDD)
- `d2`: End date (YYYYMMDD)
- `i`: Interval (d for daily)

**Response Format**: CSV
```
Date,Open,High,Low,Close,Volume
2024-01-01,150.00,152.00,149.50,151.00,1000000
```

**CSV Parsing**:
```python
df = pd.read_csv(StringIO(csv_data))
for _, row in df.iterrows():
    bar = OHLCVBar(
        time=row["Date"],
        open=row["Open"],
        high=row["High"],
        low=row["Low"],
        close=row["Close"],
        volume=row["Volume"]
    )
```

---

## CoinGecko

### Description

CoinGecko is one of the largest cryptocurrency data aggregators.

**Type**: Cryptocurrency Data  
**Authentication**: None Required (basic tier)  
**Cost**: Free tier available

### Setup

No setup required for basic usage!

### Rate Limits

**Free Tier**:
- 10-30 requests per minute (dynamic)
- No API key needed
- Rate limits may vary

**Pro API** (optional):
- Dedicated support
- Higher rate limits
- Commercial use license

### Supported Symbols

**Major Cryptocurrencies**:
- BTC (Bitcoin)
- ETH (Ethereum)
- USDT (Tether)
- BNB (Binance Coin)
- SOL (Solana)
- XRP (Ripple)
- ADA (Cardano)
- DOGE (Dogecoin)
- And 10,000+ more

### Symbol Mapping

The adapter includes built-in mapping for popular symbols:

```python
SYMBOL_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    # ... etc
}
```

For unlisted symbols, the adapter tries lowercase conversion.

### Features

- OHLC data up to 365 days
- No authentication for basic use
- Wide cryptocurrency coverage
- USD conversion built-in

### Data Quality

✅ **Pros**:
- No API key needed
- Extensive cryptocurrency coverage
- Good documentation
- Reliable uptime

❌ **Cons**:
- No volume in OHLC endpoint (returns 0)
- Rate limits can be hit quickly
- Symbol mapping required

### Example Usage

```python
adapter = CoinGeckoAdapter()
result = await adapter.fetch_ohlcv("BTC", days=90)
```

### Troubleshooting

**Error: "Symbol not recognized"**
- Solution: Use common symbols (BTC, ETH, SOL)
- Check symbol mapping in code
- Try full coin ID (e.g., "bitcoin" instead of "BTC")

**Error: "Rate limit exceeded"**
- Solution: Wait 1-2 minutes
- Consider Pro API for higher limits

**Volume is 0**
- This is expected - OHLC endpoint doesn't include volume
- Use different endpoint for volume data

### Implementation Details

**File**: `backend/adapters/coingecko.py`

**API Endpoint**: `https://api.coingecko.com/api/v3/coins/{id}/ohlc`

**Parameters**:
- `vs_currency`: usd
- `days`: Number of days (1, 7, 14, 30, 90, 180, 365, max)

**Response Format**: JSON Array
```json
[
  [1640995200000, 47000, 48000, 46500, 47500],
  // [timestamp, open, high, low, close]
]
```

**Coin ID Resolution**:
1. Check SYMBOL_MAP for known symbols
2. Fallback to lowercase symbol
3. Make API request with resolved ID

---

## CoinMarketCap

### Description

CoinMarketCap is one of the most popular cryptocurrency data providers.

**Type**: Cryptocurrency Data  
**Authentication**: API Key Required  
**Cost**: Free tier available

### Setup

1. **Get API Key**:
   - Visit: https://coinmarketcap.com/api/
   - Sign up for free account
   - Navigate to API section
   - Copy your API key

2. **Configure**:
   ```bash
   # In .env file
   COINMARKETCAP_API_KEY=your_actual_key_here
   ```

### Rate Limits

**Free Tier**:
- 10,000 credits per month
- 333 credits per day average
- Each call consumes 1-2 credits
- Credit card not required

**Paid Tiers**:
- Hobbyist: 40,000 credits/month ($29/month)
- Startup: 200,000 credits/month ($79/month)
- Professional: More credits ($299/month)

### Important Limitation

⚠️ **Free Tier Limitation**: Historical OHLCV data requires a paid plan. The free tier only provides:
- Current price quotes
- 24-hour change percentage
- Current volume

The adapter creates a single-day approximation using current data.

### Supported Symbols

All major cryptocurrencies:
- BTC, ETH, BNB, XRP, ADA, SOL, DOGE, DOT, MATIC, and more
- 9,000+ cryptocurrencies total

### Features

- Professional-grade data
- Latest price quotes (free tier)
- Historical OHLCV (paid tier)
- Market cap rankings
- Detailed metadata

### Data Quality

✅ **Pros**:
- Professional data quality
- Extensive cryptocurrency coverage
- Good API documentation
- Generous free tier credits

❌ **Cons**:
- Requires API key
- Historical data needs paid plan
- Credit system can be confusing

### Example Usage

```python
adapter = CoinMarketCapAdapter(api_key="your_key")
result = await adapter.fetch_ohlcv("BTC", days=90)
```

### Troubleshooting

**Error: "API key not configured"**
- Solution: Add key to `.env` file
- Ensure key is valid

**Error: "Symbol not found"**
- Solution: Use standard ticker symbols (BTC, ETH)
- Check spelling

**Only one data point returned**
- This is expected on free tier
- Historical data requires paid plan
- Consider using CoinGecko for historical data

**Credits depleted**
- Monitor usage on CoinMarketCap dashboard
- Wait for monthly reset
- Consider upgrading plan

### Implementation Details

**File**: `backend/adapters/coinmarketcap.py`

**API Endpoints**:
- Map: `/v1/cryptocurrency/map` (get coin ID from symbol)
- Quotes: `/v1/cryptocurrency/quotes/latest` (current data)

**Two-Step Process**:
1. Map symbol to CoinMarketCap ID
2. Fetch current quote data

**Response Structure**:
```json
{
  "data": {
    "1": {
      "symbol": "BTC",
      "quote": {
        "USD": {
          "price": 45000,
          "volume_24h": 25000000000,
          "percent_change_24h": 2.5
        }
      }
    }
  }
}
```

---

## Adapter Comparison

| Feature | Alpha Vantage | Stooq | CoinGecko | CoinMarketCap |
|---------|--------------|-------|-----------|---------------|
| **Type** | Stocks | Stocks | Crypto | Crypto |
| **API Key** | Required | Not Required | Not Required | Required |
| **Cost** | Free tier | Free | Free tier | Free tier |
| **Rate Limit** | 25/day | None | 10-30/min | 10k credits/month |
| **Historical Data** | ✅ Full | ✅ Full | ✅ Full | ❌ Paid only |
| **Volume Data** | ✅ Yes | ✅ Yes | ❌ No (OHLC) | ✅ Yes |
| **Setup Time** | Medium | Instant | Instant | Medium |
| **Data Quality** | Excellent | Good | Excellent | Excellent |
| **Best For** | US stocks | Quick testing | Crypto OHLC | Current crypto prices |

---

## Adding Custom Adapters

### Step-by-Step Guide

1. **Create new adapter file** in `backend/adapters/`:

```python
# backend/adapters/my_adapter.py
from backend.adapters.base import BaseAdapter
from backend.models import OHLCVBar, AdapterResponse

class MyAdapter(BaseAdapter):
    def __init__(self, api_key=None):
        super().__init__("My Adapter", api_key)
    
    async def fetch_ohlcv(self, symbol: str, days: int = 90) -> AdapterResponse:
        try:
            # Implement your data fetching logic
            data = await self._fetch_from_api(symbol, days)
            
            # Convert to OHLCV bars
            bars = [
                OHLCVBar(
                    time=item["date"],
                    open=item["open"],
                    high=item["high"],
                    low=item["low"],
                    close=item["close"],
                    volume=item["volume"]
                )
                for item in data
            ]
            
            return self._create_response(
                symbol=symbol,
                success=True,
                data=bars,
                rate_limit_info="Your rate limit info"
            )
            
        except Exception as e:
            return self._create_response(
                symbol=symbol,
                success=False,
                error=str(e)
            )
```

2. **Register in `__init__.py`**:

```python
# backend/adapters/__init__.py
from backend.adapters.my_adapter import MyAdapter

__all__ = [..., 'MyAdapter']
```

3. **Add to main.py**:

```python
# backend/main.py
from backend.adapters import MyAdapter

adapters = {
    "stocks": [
        AlphaVantageAdapter(...),
        StooqAdapter(),
        MyAdapter(),  # Add here
    ],
    ...
}
```

### Best Practices

1. **Error Handling**: Always catch exceptions and return proper error responses
2. **Rate Limiting**: Include rate limit information in responses
3. **Data Validation**: Validate data before creating OHLCV bars
4. **Async Operations**: Use async/await for network requests
5. **Timeouts**: Set appropriate timeouts (30 seconds recommended)
6. **Documentation**: Add docstrings and comments

### Testing Your Adapter

```python
# Quick test script
import asyncio
from backend.adapters.my_adapter import MyAdapter

async def test():
    adapter = MyAdapter(api_key="test_key")
    result = await adapter.fetch_ohlcv("BTC", 30)
    print(result)

asyncio.run(test())
```

---

## Common Issues Across All Adapters

### Network Issues

**Problem**: Timeout errors  
**Solution**:
- Check internet connection
- Increase timeout in adapter code
- Retry with exponential backoff

### Rate Limiting

**Problem**: Too many requests  
**Solution**:
- Wait before retrying
- Implement caching
- Use multiple API keys (rotate)

### Data Quality

**Problem**: Missing or invalid data  
**Solution**:
- Validate data before using
- Handle edge cases (weekends, holidays)
- Use fallback adapters

---

## Recommendations

### For Stock Data
1. **Development**: Use Stooq (no setup, unlimited)
2. **Production**: Use Alpha Vantage (better quality, limited but reliable)
3. **Alternative**: Consider Yahoo Finance (yfinance library)

### For Crypto Data
1. **Development**: Use CoinGecko (no setup, good coverage)
2. **Production**: Use CoinGecko for historical, CoinMarketCap for current
3. **Alternative**: Consider Binance API for real-time data

### General Tips
- Always implement error handling
- Display clear error messages to users
- Show rate limit information
- Allow users to retry failed requests
- Cache successful responses

---

## Resources

### Official Documentation

- **Alpha Vantage**: https://www.alphavantage.co/documentation/
- **Stooq**: https://stooq.com/ (no official API docs)
- **CoinGecko**: https://www.coingecko.com/en/api/documentation
- **CoinMarketCap**: https://coinmarketcap.com/api/documentation/v1/

### Community Resources

- **Stack Overflow**: Search for adapter-specific questions
- **Reddit**: r/algotrading, r/quantfinance
- **GitHub**: Check for existing implementations

### Alternative Data Sources

- Yahoo Finance (yfinance)
- IEX Cloud
- Polygon.io
- Finnhub
- Twelve Data
- Quandl/Nasdaq Data Link

---

## Support

For adapter-specific issues:
1. Check this documentation
2. Review the adapter source code
3. Check official API documentation
4. Test with simple examples
5. Review error messages carefully

For feature requests or new adapter suggestions, open an issue in the repository.
