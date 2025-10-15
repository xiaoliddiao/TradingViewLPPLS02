#!/usr/bin/env python3
"""Quick test script to verify all adapters and API endpoints"""
import asyncio
import sys
sys.path.insert(0, '/Users/leo/Documents/GitHub/TradingViewLPPLS02')

from app.services import fetch_all_adapters


async def test_symbols():
    symbols = ['BTC', 'ETH', 'AAPL', 'TSLA', 'MSFT']
    
    print("=" * 60)
    print("API ADAPTER TEST")
    print("=" * 60)
    print()
    
    for symbol in symbols:
        print(f"Testing {symbol}...")
        data, status = await fetch_all_adapters(symbol)
        
        success_count = sum(1 for s in status.values() if s == 'ok')
        total = len(status)
        
        print(f"  Status: {success_count}/{total} adapters successful")
        
        for name, stat in status.items():
            icon = "✅" if stat == "ok" else "❌"
            points = len(data.get(name, []))
            if points > 0:
                print(f"    {icon} {name}: {points} data points")
            else:
                print(f"    {icon} {name}: {stat}")
        print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ Yahoo Finance: Best source for stocks & crypto (no key needed)")
    print("✅ CoinGecko: Good backup for crypto (no key needed)")
    print("⚠️  Alpha Vantage: Requires API key")
    print("⚠️  Stooq: Limited coverage")
    print("⚠️  CoinMarketCap: Requires API key")
    print()
    print("🌐 Open http://localhost:8000/static/index.html to view charts")


if __name__ == '__main__':
    asyncio.run(test_symbols())

