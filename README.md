# 📈 Trading Data Aggregator

A production-ready quantitative trading application that fetches daily OHLCV (Open, High, Low, Close, Volume) data from multiple free and low-cost data sources and visualizes them using TradingView Lightweight Charts.

## Features

- **Multi-Source Data Aggregation**: Fetch data from 4 different providers simultaneously
  - **Stocks**: Alpha Vantage, Stooq
  - **Crypto**: CoinGecko, CoinMarketCap
  
- **Real-Time Status Indicators**: Visual feedback showing which adapters succeeded (✓) or failed (✗)

- **Professional Charts**: Full-featured TradingView Lightweight Charts with:
  - Multiple chart types (Candlestick, Line, Area, Bar)
  - Zoom and pan functionality
  - Crosshair with price/time information
  - Responsive design

- **Clean Architecture**: Modular, pluggable adapter system for easy extension

## Quick Start (macOS)

### Prerequisites

- Python 3.9 or higher (Python 3.13 recommended)
- pip (Python package manager)

### Installation

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

**Quick setup:**

1. **Navigate to the project directory**

```bash
cd /path/to/trading-data-aggregator
```

2. **Create and activate virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure API keys** (Optional - CoinGecko and Stooq work without keys!)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Get a free Alpha Vantage key at: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Get a free CoinMarketCap key at: https://coinmarketcap.com/api/
COINMARKETCAP_API_KEY=your_coinmarketcap_key_here
```

**Note**: Stooq and CoinGecko work without API keys!

### Running the Application

1. **Start the server**

```bash
python3 -m uvicorn backend.main:app --reload
```

Or use the convenient script:

```bash
./run.sh
```

2. **Open your browser**

Navigate to: [http://localhost:8000](http://localhost:8000)

3. **Test the application**

- The default symbol is "BTC" (Bitcoin)
- Click "Fetch Data" to retrieve data from all sources
- See which adapters successfully fetched data (✓) or failed (✗)
- View the candlestick chart with interactive controls

## Usage Examples

### Testing Different Symbols

**Cryptocurrencies** (work best with CoinGecko and CoinMarketCap):
- BTC (Bitcoin)
- ETH (Ethereum)
- SOL (Solana)
- AVAX (Avalanche)

**Stocks** (work with Alpha Vantage and Stooq):
- AAPL (Apple) - Try with Alpha Vantage
- AAPL.US (Apple) - Try with Stooq
- MSFT (Microsoft)
- GOOGL (Google)

### Chart Interactions

- **Zoom**: Scroll to zoom in/out
- **Pan**: Click and drag to move through time
- **Chart Type**: Switch between Candlestick, Line, Area, and Bar
- **Data Source**: Select which adapter's data to display
- **Crosshair**: Hover to see exact values

## API Endpoints

### `POST /api/fetch`

Fetch OHLCV data from all adapters.

**Request Body**:
```json
{
  "symbol": "BTC",
  "days": 90
}
```

**Response**:
```json
{
  "symbol": "BTC",
  "results": [
    {
      "adapter_name": "CoinGecko",
      "symbol": "BTC",
      "success": true,
      "data": [...],
      "rate_limit_info": "Free tier: 10-30 requests/minute"
    },
    ...
  ]
}
```

### `GET /api/health`

Health check endpoint.

### `GET /api/adapters`

List all available adapters and their configuration status.

## Project Structure

```
trading-data-aggregator/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic data models
│   └── adapters/
│       ├── __init__.py
│       ├── base.py             # Base adapter interface
│       ├── alpha_vantage.py    # Alpha Vantage adapter
│       ├── stooq.py            # Stooq adapter
│       ├── coingecko.py        # CoinGecko adapter
│       └── coinmarketcap.py    # CoinMarketCap adapter
├── frontend/
│   ├── index.html              # Main HTML page
│   ├── styles.css              # Styling
│   └── app.js                  # Frontend JavaScript
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── DECISIONS.md               # Design decisions
├── CHANGELOG.md               # Version history
└── ADAPTERS.md                # Adapter documentation
```

## Troubleshooting

### No data from any source

1. Check your internet connection
2. Verify API keys are correctly set in `.env`
3. Check rate limits (wait a minute and try again)
4. Try a different symbol

### Specific adapter failing

See the error message in the adapter status card. Common issues:
- **Alpha Vantage**: API key not set or rate limit exceeded (25 requests/day)
- **Stooq**: Symbol format incorrect (try adding .US suffix for US stocks)
- **CoinGecko**: Symbol not recognized (check supported symbols)
- **CoinMarketCap**: API key not set or free tier limitations

### Chart not displaying

1. Ensure at least one adapter succeeded
2. Check browser console for JavaScript errors
3. Try refreshing the page

## Development

### Deactivating Virtual Environment

```bash
deactivate
```

### Running Tests

```bash
pytest  # (if tests are added)
```

### Adding a New Adapter

1. Create a new file in `backend/adapters/`
2. Inherit from `BaseAdapter`
3. Implement the `fetch_ohlcv()` method
4. Add to `backend/adapters/__init__.py`
5. Register in `backend/main.py`

See `ADAPTERS.md` for detailed adapter documentation.

## License

MIT License - Feel free to use this project for learning and production.

## Credits

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Charts powered by [TradingView Lightweight Charts](https://www.tradingview.com/lightweight-charts/)
- Data from Alpha Vantage, Stooq, CoinGecko, and CoinMarketCap

## Support

For issues and questions, please check:
- `DECISIONS.md` for design rationale
- `ADAPTERS.md` for adapter-specific documentation
- `CHANGELOG.md` for recent changes
