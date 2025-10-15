# Quick Start Guide

## ⚡ 60-Second Setup

```bash
# 1. Install dependencies
pip3 install --user -r requirements.txt

# 2. Start the server
python3 -m uvicorn backend.main:app --reload

# 3. Open browser
# → http://localhost:8000
```

Done! 🎉

---

## 🎯 First Test

1. **Default test**: Click "Fetch Data" (BTC is pre-filled)
2. **Watch**: CoinGecko and Stooq will fetch data ✓
3. **See**: Candlestick chart displays immediately
4. **Try**: Change chart type, zoom, pan

---

## 🔑 Optional: Add API Keys

```bash
# Copy template
cp .env.example .env

# Edit .env and add your keys
nano .env
```

Get free keys:
- Alpha Vantage: https://www.alphavantage.co/support/#api-key
- CoinMarketCap: https://coinmarketcap.com/api/

**Note**: Not required! CoinGecko and Stooq work without keys.

---

## 📊 Test Symbols

### Crypto (Works with CoinGecko)
- `BTC` - Bitcoin
- `ETH` - Ethereum  
- `SOL` - Solana
- `AVAX` - Avalanche

### Stocks (Works with Stooq)
- `AAPL.US` - Apple
- `MSFT.US` - Microsoft
- `GOOGL.US` - Google
- `TSLA.US` - Tesla

**Note**: Stooq requires `.US` suffix for US stocks

---

## 🛠️ Chart Features

- **Zoom**: Scroll wheel
- **Pan**: Click and drag
- **Types**: Candlestick, Line, Area, Bar
- **Sources**: Switch between working adapters
- **Info**: Hover for price/time details

---

## 📁 Project Files

```
trading-data-aggregator/
├── backend/          # FastAPI backend
│   ├── main.py       # API endpoints
│   ├── models.py     # Data models
│   └── adapters/     # Data source adapters
├── frontend/         # Web interface
│   ├── index.html    # Main page
│   ├── styles.css    # Styling
│   └── app.js        # Chart logic
└── docs/
    ├── README.md     # Full documentation
    ├── INSTALL.md    # Detailed install
    ├── ADAPTERS.md   # Adapter docs
    └── DECISIONS.md  # Architecture
```

---

## 🐛 Troubleshooting

### Port in use?
```bash
python3 -m uvicorn backend.main:app --reload --port 8080
# Then use http://localhost:8080
```

### No data?
- CoinGecko works without API keys ✓
- Stooq works without API keys ✓  
- Try different symbols
- Check network connection

### Import errors?
```bash
pip3 install --user -r requirements.txt
```

---

## 📚 Learn More

- `README.md` - Complete guide
- `INSTALL.md` - Detailed installation
- `ADAPTERS.md` - Data source info
- `DECISIONS.md` - Why we built it this way

---

## 🚀 Ready for More?

**Add your own adapter:**
1. Copy `backend/adapters/base.py`
2. Implement `fetch_ohlcv()`
3. Register in `backend/main.py`

**Deploy to production:**
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

**That's it! Happy trading! 📈**
