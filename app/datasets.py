from __future__ import annotations
import os
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timezone

import numpy as np
import pandas as pd

OHLCV = Dict[str, float]

DATASET_DIR_ENV = "DATASET_DIR"
DEFAULT_CANDIDATE_DIRS = [
    "/workspace/stooq_nasdaq stocksdata_H_day_72_fortest",
    "/workspace/data/stooq_nasdaq stocksdata_H_day_72_fortest",
    "/workspace/data/stooq_nasdaq_stocksdata_H_day_72_fortest",
    "/workspace/stooq_nasdaq_stocksdata_H_day_72_fortest",
]


def _detect_dataset_dir() -> Optional[str]:
    # 1. Env override
    env_dir = os.getenv(DATASET_DIR_ENV)
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    # 2. Known candidates
    for d in DEFAULT_CANDIDATE_DIRS:
        if os.path.isdir(d):
            return d
    # 3. Heuristic search under /workspace for a dir containing 50+ .txt files
    for root, dirs, files in os.walk("/workspace"):
        txt_count = sum(1 for f in files if f.lower().endswith(".txt"))
        if txt_count >= 50:
            return root
    return None


def list_dataset_files() -> List[str]:
    base = _detect_dataset_dir()
    if not base:
        return []
    files = [os.path.join(base, f) for f in os.listdir(base) if f.lower().endswith(".txt")]
    files.sort()
    return files


def _parse_date(value: str) -> Optional[int]:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            dt = datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except Exception:
            continue
    # maybe epoch seconds
    if re.fullmatch(r"\d{10}", value):
        try:
            return int(value)
        except Exception:
            pass
    return None


def read_dataset_candles_by_index(index: int) -> Tuple[str, str, List[OHLCV]]:
    files = list_dataset_files()
    if not files or index < 0 or index >= len(files):
        raise FileNotFoundError("dataset file not found")
    path = files[index]
    return read_dataset_candles_by_path(path)


def read_dataset_candles_by_path(path: str) -> Tuple[str, str, List[OHLCV]]:
    # Load with pandas auto-sep
    df = pd.read_csv(path, sep=None, engine="python")
    # Normalize columns
    cols = {c.lower().strip(): c for c in df.columns}
    # Try to locate date
    date_col = None
    for key in ("date", "time", "timestamp"):
        if key in cols:
            date_col = cols[key]
            break
    if date_col is None:
        # assume first column is date-like
        date_col = df.columns[0]
    # Try OHLCV
    def find_col(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None
    open_col = find_col("open", "o")
    high_col = find_col("high", "h")
    low_col = find_col("low", "l")
    close_col = find_col("close", "c") or find_col("adj close", "adj_close", "adjclose")
    vol_col = find_col("volume", "vol", "v")

    # If only close provided, synthesize OHLC around close
    if close_col is None and df.shape[1] >= 5:
        # assume order Date,Open,High,Low,Close,(Volume)
        date_col = df.columns[0]
        open_col = df.columns[1]
        high_col = df.columns[2]
        low_col = df.columns[3]
        close_col = df.columns[4]
        vol_col = df.columns[5] if df.shape[1] >= 6 else None

    times: List[int] = []
    opens: List[float] = []
    highs: List[float] = []
    lows: List[float] = []
    closes: List[float] = []
    vols: List[float] = []

    for _, row in df.iterrows():
        t_raw = row[date_col]
        if pd.isna(t_raw):
            continue
        if isinstance(t_raw, (int, float)) and not isinstance(t_raw, bool):
            # treat as ordinal day or epoch seconds; assume epoch if large
            t_val = int(t_raw)
            if t_val > 10_000_000:  # likely epoch seconds
                ts = t_val
            else:
                # ordinal-ish: convert days to seconds from a base (1970-01-01)
                ts = int(t_val) * 86400
        else:
            ts = _parse_date(str(t_raw)) or 0
        if ts == 0:
            continue
        o = float(row[open_col]) if open_col in df.columns else float(row[close_col])
        h = float(row[high_col]) if high_col in df.columns else float(row[close_col])
        l = float(row[low_col]) if low_col in df.columns else float(row[close_col])
        c = float(row[close_col]) if close_col in df.columns else float(row[open_col])
        v = float(row[vol_col]) if vol_col in df.columns else 0.0
        times.append(ts)
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
        vols.append(v)

    # Sort by time
    order = np.argsort(times)
    times = [times[i] for i in order]
    opens = [opens[i] for i in order]
    highs = [highs[i] for i in order]
    lows = [lows[i] for i in order]
    closes = [closes[i] for i in order]
    vols = [vols[i] for i in order]

    data: List[OHLCV] = []
    for t, o, h, l, c, v in zip(times, opens, highs, lows, closes, vols):
        data.append({
            "time": int(t),
            "open": float(o),
            "high": float(h),
            "low": float(l),
            "close": float(c),
            "volume": float(v),
        })

    symbol = os.path.splitext(os.path.basename(path))[0]
    return path, symbol, data


def times_epoch_to_index_mapping(times: List[int]) -> Tuple[np.ndarray, float]:
    """Return index-based time vector (0..n-1) and median step seconds for mapping back."""
    n = len(times)
    t_idx = np.arange(n, dtype=float)
    # median step in epoch seconds
    if n >= 2:
        diffs = np.diff(np.array(times, dtype=float))
        step = float(np.median(diffs))
    else:
        step = 86400.0
    return t_idx, step
