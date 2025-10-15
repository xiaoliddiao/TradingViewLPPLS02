# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-15

### Added

#### Core Features
- **Multi-Source Data Aggregation**: Simultaneous fetching from 4 data providers
  - Alpha Vantage (stocks)
  - Stooq (stocks)
  - CoinGecko (crypto)
  - CoinMarketCap (crypto)

- **Interactive TradingView Charts**:
  - Candlestick chart type
  - Line chart type
  - Area chart type
  - Bar chart type
  - Zoom and pan functionality
  - Crosshair with price/time information
  - Responsive design

- **Real-Time Status Indicators**:
  - Visual success (✓) and failure (✗) indicators
  - Error messages for failed adapters
  - Rate limit information display

#### Backend Architecture
- FastAPI-based REST API
- Async/await for concurrent data fetching
- Pydantic models for data validation
- Base adapter interface for extensibility
- Environment variable configuration

#### Frontend
- Clean, modern dark theme UI
- Responsive grid layout for adapter status
- Dynamic data source switching
- Chart type selection
- Symbol and date range inputs

#### Documentation
- Comprehensive README with macOS installation guide
- DECISIONS.md explaining architecture and design choices
- ADAPTERS.md with detailed adapter documentation
- .env.example for easy configuration

#### Development Tools
- Requirements.txt with pinned versions
- .gitignore for Python projects
- Virtual environment setup instructions

### Technical Details

#### API Endpoints
- `POST /api/fetch` - Fetch OHLCV data from all adapters
- `GET /api/health` - Health check endpoint
- `GET /api/adapters` - List available adapters

#### Adapter Features
- **Alpha Vantage**:
  - Daily time series data
  - Configurable output size
  - Rate limit handling
  - API key authentication

- **Stooq**:
  - CSV data parsing
  - No authentication required
  - Date range support
  - Symbol format flexibility

- **CoinGecko**:
  - OHLC endpoint integration
  - Symbol mapping for popular cryptocurrencies
  - No authentication required
  - Up to 365 days of data

- **CoinMarketCap**:
  - Cryptocurrency ID mapping
  - Current quote data (free tier)
  - API key authentication
  - Rate limit tracking

#### Frontend Technologies
- Vanilla JavaScript (no frameworks)
- TradingView Lightweight Charts 4.1.0
- CSS Grid and Flexbox layouts
- Fetch API for HTTP requests

### Dependencies

#### Python Packages
- `fastapi==0.104.1` - Web framework
- `uvicorn==0.24.0` - ASGI server
- `httpx==0.25.1` - Async HTTP client
- `pydantic==2.5.0` - Data validation
- `python-dotenv==1.0.0` - Environment variables
- `pandas==2.1.3` - Data manipulation
- `numpy==1.26.2` - Numerical operations
- `aiohttp==3.9.1` - Async HTTP (alternative client)

### Security
- API keys stored in environment variables
- .env file excluded from git
- CORS middleware for development
- Input validation with Pydantic

### Performance
- Concurrent API requests with asyncio.gather
- Async I/O throughout the stack
- Efficient chart rendering with TradingView library
- Connection pooling with httpx

### Known Limitations (v1.0.0)
- CoinMarketCap free tier only provides current quote (not historical OHLCV)
- Alpha Vantage limited to 25 requests per day
- No caching layer (every request hits external APIs)
- No authentication/authorization
- No persistent storage
- Stooq requires .US suffix for US stocks

### Future Enhancements (Planned)
- [ ] Add caching layer (Redis)
- [ ] Additional data sources (Yahoo Finance, Finnhub)
- [ ] User authentication
- [ ] Real-time data with WebSockets
- [ ] Technical indicators
- [ ] Backtesting engine
- [ ] Unit and integration tests
- [ ] Docker containerization
- [ ] CI/CD pipeline

---

## Version History

### [1.0.0] - 2025-10-15
- Initial production-ready release
- Core features complete
- Documentation complete
- Ready for deployment

---

## Migration Guide

### Upgrading from Pre-release

This is the first official release. No migration needed.

### Environment Variables

If you're setting up for the first time:

1. Copy `.env.example` to `.env`
2. Add your API keys:
   - `ALPHA_VANTAGE_API_KEY` (optional)
   - `COINMARKETCAP_API_KEY` (optional)

### Database Schema

No database required in v1.0.0.

---

## Breaking Changes

None (initial release).

---

## Contributors

- Initial development and architecture
- Adapter implementations
- Frontend design and implementation
- Documentation

---

## Support and Feedback

For issues, questions, or feature requests:
- Check the documentation files (README, DECISIONS, ADAPTERS)
- Review this changelog for recent changes
- Open an issue in the repository

---

## License

MIT License - See LICENSE file for details.
