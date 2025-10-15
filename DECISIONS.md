### Design and rationale

- Pluggable adapters
  - Each provider implements `fetch_daily_ohlcv(symbol)` returning array of `{time, open, high, low, close, volume}` with `time` in UNIX seconds.
  - This uniform shape feeds TradingView Lightweight Charts.

- Concurrency
  - The backend concurrently fetches all providers and returns per-source `status` alongside `data`.
  - The frontend shows ✓/✗ per provider and renders the first successful dataset immediately for snappy UX.

- Frontend
  - Static HTML + Lightweight Charts. Timezone selection updates chart localization. Volume histogram is shown on left scale.

- Reliability
  - API keys optional; adapters handle missing keys and may return errors. The UI remains usable if some providers fail.

- Version pinning
  - Python deps are pinned for reproducibility. No bundler needed for the static frontend.
