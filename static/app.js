const providers = [
  { key: 'alpha_vantage', label: 'Alpha Vantage' },
  { key: 'stooq', label: 'Stooq' },
  { key: 'coingecko', label: 'CoinGecko' },
  { key: 'coinmarketcap', label: 'CoinMarketCap' },
];

function setStatus(key, status) {
  const el = document.getElementById(`status-${key}`);
  if (!el) return;
  el.textContent = status === 'ok' ? '✅' : status === 'error' ? '❌' : '⏳';
}

function toTVData(candles) {
  return candles.map(c => ({
    time: Math.floor(c.time),
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
  }));
}

function renderChart(key, candles, timezone) {
  const container = document.getElementById(`chart-${key}`);
  container.innerHTML = '';
  const chart = LightweightCharts.createChart(container, {
    layout: { background: { type: 'solid', color: '#0f172a' }, textColor: '#e6edf3' },
    grid: { vertLines: { color: '#1f2937' }, horzLines: { color: '#1f2937' } },
    timeScale: { timeVisible: true, secondsVisible: false, borderColor: '#263245' },
    rightPriceScale: { borderColor: '#263245' },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    watermark: { visible: true, text: key, color: 'rgba(180, 180, 180, 0.2)', fontSize: 18 },
    localization: { timezone },
  });
  const series = chart.addCandlestickSeries();
  series.setData(toTVData(candles));
}

async function fetchProvider(key, symbol) {
  setStatus(key, 'loading');
  try {
    const res = await fetch(`/api/ohlcv/${key}?symbol=${encodeURIComponent(symbol)}`);
    const data = await res.json();
    if (data && data.candles && data.candles.length > 0) {
      setStatus(key, 'ok');
      const tz = document.getElementById('timezoneSelect').value;
      renderChart(key, data.candles, tz);
    } else {
      setStatus(key, 'error');
    }
  } catch (e) {
    setStatus(key, 'error');
  }
}

async function loadAll() {
  const symbol = document.getElementById('symbolInput').value.trim() || 'BTC';
  providers.forEach(p => setStatus(p.key, 'loading'));
  await Promise.all(providers.map(p => fetchProvider(p.key, symbol)));
}

document.getElementById('loadBtn').addEventListener('click', loadAll);
document.getElementById('timezoneSelect').addEventListener('change', () => {
  // re-render charts with selected timezone by reloading data (keeps it simple)
  loadAll();
});

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('symbolInput').value = 'BTC';
  loadAll();
});

