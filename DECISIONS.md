# Design Decisions and Architecture

This document explains the key design decisions, architecture choices, and principles behind the Trading Data Aggregator.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Design Patterns](#design-patterns)
4. [Data Flow](#data-flow)
5. [API Design](#api-design)
6. [Frontend Architecture](#frontend-architecture)
7. [Security Considerations](#security-considerations)
8. [Performance Optimizations](#performance-optimizations)
9. [Future Enhancements](#future-enhancements)

---

## Architecture Overview

### Separation of Concerns

The application follows a clean architecture with clear separation between:

- **Backend (Python/FastAPI)**: Data fetching, adapter orchestration, API endpoints
- **Frontend (HTML/CSS/JS)**: User interface, chart rendering, user interactions
- **Adapters (Plugin System)**: Isolated data source integrations

### Why This Architecture?

1. **Modularity**: Each adapter is independent and can be developed/tested separately
2. **Extensibility**: New data sources can be added without modifying core logic
3. **Maintainability**: Clear boundaries make the codebase easy to understand and modify
4. **Testability**: Each component can be unit tested in isolation

---

## Technology Stack

### Backend: FastAPI

**Why FastAPI?**

- **Modern Python**: Uses Python 3.9+ features (type hints, async/await)
- **High Performance**: Built on Starlette and Pydantic, comparable to Node.js and Go
- **Automatic Documentation**: Auto-generated OpenAPI/Swagger docs
- **Type Safety**: Pydantic models provide runtime validation
- **Async Support**: Native async/await for concurrent API calls

**Alternatives Considered**:
- Flask: Simpler but lacks native async and type validation
- Django: Too heavy for this use case
- Node.js/Express: Would work but team expertise is in Python

### Frontend: Vanilla JavaScript + TradingView Lightweight Charts

**Why Vanilla JS?**

- **Simplicity**: No build step required
- **Performance**: No framework overhead
- **Learning**: Easier to understand and modify
- **Lightweight**: Minimal dependencies

**Why TradingView Lightweight Charts?**

- **Professional**: Industry-standard charting library
- **Feature-Rich**: Supports multiple chart types, zoom, pan, crosshair
- **Performance**: Optimized for rendering large datasets
- **Free**: Open-source and free to use

**Alternatives Considered**:
- Chart.js: Good but less feature-rich for financial charts
- D3.js: Powerful but requires more custom code
- Plotly: Great but heavier library

### Data Models: Pydantic

**Why Pydantic?**

- **Validation**: Automatic data validation at runtime
- **Documentation**: Self-documenting with type hints
- **Serialization**: Easy JSON conversion
- **FastAPI Integration**: Native support in FastAPI

---

## Design Patterns

### 1. Adapter Pattern

**Implementation**: `BaseAdapter` abstract class with concrete implementations

**Benefits**:
- Uniform interface for all data sources
- Easy to add new sources
- Consistent error handling
- Swappable implementations

**Example**:
```python
class BaseAdapter(ABC):
    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, days: int) -> AdapterResponse:
        pass
```

### 2. Strategy Pattern

**Implementation**: Interchangeable adapters selected at runtime

**Benefits**:
- Client code doesn't care which adapter is used
- Easy to switch between data sources
- Parallel fetching from multiple sources

### 3. Factory Pattern

**Implementation**: Adapter initialization in `main.py`

**Benefits**:
- Centralized adapter configuration
- Environment-based initialization (API keys from `.env`)
- Easy to mock for testing

---

## Data Flow

### Request Flow

1. **User Input** → Symbol entered in frontend
2. **Frontend** → POST request to `/api/fetch`
3. **Backend** → Parallel fetch from all adapters
4. **Adapters** → External API calls
5. **Backend** → Aggregate results
6. **Frontend** → Update UI and chart

### Concurrent Fetching

```python
tasks = [adapter.fetch_ohlcv(symbol, days) for adapter in all_adapters]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

**Why Parallel?**
- Faster response time (4 requests in parallel vs sequential)
- Better user experience
- Timeout isolation (one slow adapter doesn't block others)

### Error Handling

- **Graceful Degradation**: If one adapter fails, others still work
- **Explicit Errors**: Each adapter returns success/failure status
- **User Feedback**: Clear error messages displayed in UI

---

## API Design

### RESTful Principles

- `GET /api/health` - Health check (idempotent, cacheable)
- `POST /api/fetch` - Fetch data (not idempotent, body contains parameters)
- `GET /api/adapters` - List adapters (idempotent, cacheable)

### Request/Response Models

**Structured Data**:
- Request: `MultiAdapterRequest` (symbol, days)
- Response: `MultiAdapterResponse` (symbol, results[])
- Adapter Response: `AdapterResponse` (adapter_name, success, data, error)

**Benefits**:
- Type safety
- Automatic validation
- Self-documenting API

### Rate Limiting Strategy

**Implemented at Adapter Level**:
- Each adapter returns `rate_limit_info`
- Frontend displays limits to users
- No backend rate limiting (relies on external API limits)

**Why?**
- Simple for MVP
- Transparent to users
- Different limits for different adapters

**Future**: Could add backend caching to reduce external API calls

---

## Frontend Architecture

### Component Structure

**Single-Page Application**:
- No routing needed
- All interactions on one page
- Simple state management

### State Management

**Class-Based Approach**:
```javascript
class TradingApp {
    constructor() {
        this.chart = null;
        this.currentData = {};
        this.currentSymbol = 'BTC';
    }
}
```

**Benefits**:
- Encapsulated state
- Clear ownership
- Easy to reason about

### Chart Management

**Separation of Concerns**:
- Chart initialization separate from data updates
- Series switching logic isolated
- Responsive design built-in

---

## Security Considerations

### API Keys

**Storage**: Environment variables (`.env` file)
- Not committed to git (`.gitignore`)
- Server-side only (never exposed to frontend)
- Example file (`.env.example`) for setup

### CORS

**Enabled for Development**:
```python
allow_origins=["*"]
```

**Production**: Should restrict to specific origins

### Input Validation

**Pydantic Models**:
- Symbol: string
- Days: integer, range [1, 365]
- Automatic validation prevents invalid requests

### No Authentication (MVP)

**Current**: Open API
**Future**: Add API keys, OAuth, rate limiting per user

---

## Performance Optimizations

### 1. Async I/O

- All network requests use `httpx.AsyncClient`
- Concurrent adapter fetching with `asyncio.gather`
- Non-blocking server with `uvicorn`

### 2. Frontend Optimizations

- TradingView Lightweight Charts optimized for large datasets
- Lazy loading (chart only renders visible data)
- Efficient DOM updates

### 3. Data Caching

**Current**: No caching
**Future**: 
- Redis for response caching
- Browser localStorage for recent queries
- Configurable TTL per adapter

### 4. Connection Pooling

- `httpx.AsyncClient` reuses connections
- Reduces latency for repeated requests

---

## Data Source Selection

### Stocks

**Alpha Vantage**:
- ✅ Free tier available
- ✅ Good data quality
- ❌ Low rate limit (25/day)
- ❌ Requires API key

**Stooq**:
- ✅ No API key required
- ✅ No rate limits
- ✅ Simple CSV format
- ⚠️ Symbol format quirks (.US suffix)

### Crypto

**CoinGecko**:
- ✅ No API key for basic usage
- ✅ Good coverage
- ✅ OHLC endpoint
- ❌ No volume in OHLC data

**CoinMarketCap**:
- ✅ Professional data
- ✅ High rate limits
- ❌ Requires API key
- ❌ Historical OHLCV requires paid plan (free tier shows current only)

### Alternatives Considered

- **Yahoo Finance**: Unofficial API, unstable
- **IEX Cloud**: Good but paid
- **Polygon.io**: Excellent but expensive
- **Binance API**: Only crypto, complex
- **Finnhub**: Good alternative to Alpha Vantage

---

## Error Handling Philosophy

### Fail-Fast for Development

- Clear error messages
- Stack traces in development mode
- Validation errors caught early

### Graceful Degradation for Users

- Never crash the entire application
- Show partial results
- Clear indication of what failed and why

### Example Error Flow

```
User enters invalid symbol
  ↓
Backend validates (Pydantic)
  ↓
Adapters attempt fetch
  ↓
Some succeed, some fail
  ↓
Frontend shows both results
  ↓
User can see which sources worked
```

---

## Testing Strategy

### Current State (MVP)

- Manual testing with real APIs
- BTC default for smoke testing

### Future Testing

**Unit Tests**:
- Mock external API responses
- Test each adapter independently
- Pydantic model validation

**Integration Tests**:
- Test full request/response cycle
- Test concurrent adapter execution

**E2E Tests**:
- Selenium/Playwright for browser testing
- Test chart rendering
- Test user interactions

---

## Future Enhancements

### Short Term

1. **Add More Adapters**:
   - Yahoo Finance (yfinance library)
   - Twelve Data
   - Finnhub

2. **Caching Layer**:
   - Redis for API responses
   - Configurable TTL
   - Cache invalidation

3. **Better Error UX**:
   - Retry buttons
   - Suggestions for failed symbols
   - Auto-retry with backoff

### Medium Term

4. **Authentication**:
   - User accounts
   - API key management
   - Usage tracking

5. **Real-Time Data**:
   - WebSocket connections
   - Live price updates
   - Streaming charts

6. **Technical Indicators**:
   - Moving averages
   - RSI, MACD, Bollinger Bands
   - Custom indicator builder

### Long Term

7. **Backtesting Engine**:
   - Strategy builder
   - Performance metrics
   - Optimization tools

8. **Alerting System**:
   - Price alerts
   - Pattern recognition
   - Email/SMS notifications

9. **Portfolio Tracking**:
   - Multiple symbols
   - Performance analytics
   - Risk metrics

---

## Lessons Learned

### What Went Well

1. **Adapter Pattern**: Made it easy to add new sources
2. **Async/Await**: Significantly improved performance
3. **Type Hints**: Caught many bugs early
4. **TradingView Charts**: Professional results with minimal code

### What Could Be Better

1. **Testing**: Should have added tests from the start
2. **Error Messages**: Could be more specific about symbol formats
3. **Caching**: Would reduce API calls significantly
4. **Documentation**: Inline code comments could be more detailed

---

## Conclusion

This architecture prioritizes:

1. **Simplicity**: Easy to understand and modify
2. **Extensibility**: Easy to add new features
3. **Performance**: Fast response times
4. **User Experience**: Clear feedback and professional UI

The design is production-ready for MVP but has clear paths for enhancement as the project grows.
