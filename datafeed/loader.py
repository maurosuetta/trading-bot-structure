"""
loader.py — DataLoader for fetching historical data (intraday and daily) using yfinance.

Responsibilities:
- Handle Yahoo Finance constraints (interval/period).
- Download OHLCV data for a given symbol.
- Cache raw CSVs to /data/raw for reproducibility.
- Load from cache if available (to avoid repeated HTTP requests).
- Normalize datetime index to UTC.
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Optional

from config import settings


class DataLoader:
    """
    DataLoader handles downloading and caching of historical market data.

    Example:
        loader = DataLoader()
        df = loader.get("SPY", interval="5m", period="60d")
    """

    def __init__(self, raw_dir: Optional[Path] = None) -> None:
        """
        Initialize the DataLoader.

        Args:
            raw_dir: Optional override for raw data directory.
        """
        self.raw_dir = raw_dir or settings.RAW_DATA_DIR

    def _download_from_yf(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        """
        Use yfinance to download OHLCV data.

        Args:
            symbol: Yahoo ticker symbol.
            interval: Bar interval, e.g. "1m", "5m", "15m".
            period: Max lookback, e.g. "7d", "60d".

        Returns:
            DataFrame with OHLCV and DatetimeIndex in UTC.
        """
        df = yf.download(
            tickers=symbol,
            interval=interval,
            period=period,
            auto_adjust=False,   # keep raw OHLC
            progress=False,
            prepost=False        # no extended hours for equities
        )

        if df.empty:
            raise ValueError(f"No data returned for {symbol} with {interval}/{period}.")

        # Normalize index to UTC
        df.index = pd.to_datetime(df.index, utc=True)

        # Ensure standard column names
        df = df.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )

        return df

    def _cache_path(self, symbol: str, interval: str) -> Path:
        """
        Build path for cached CSV.

        Args:
            symbol: Yahoo ticker symbol.
            interval: Interval string.

        Returns:
            Path for raw CSV cache.
        """
        return settings.path_for_raw_csv(symbol, interval)

    def get(
        self,
        symbol: str,
        interval: Optional[str] = None,
        period: Optional[str] = None,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Retrieve data for a symbol. Download if cache is missing or disabled.

        Args:
            symbol: Yahoo Finance ticker (e.g. "SPY", "TSLA", "BTC-USD").
            interval: Bar interval (default from settings).
            period: Lookback period (default from settings).
            use_cache: If True, load from cache if available.

        Returns:
            Cleaned OHLCV DataFrame.
        """
        interval = interval or settings.DEFAULT_INTERVAL
        period = period or settings.yf_max_period_for_interval(interval)
        cache_file = self._cache_path(symbol, interval)

        if use_cache and cache_file.exists():
            df = pd.read_csv(cache_file, parse_dates=True, index_col=0)
            df.index = pd.to_datetime(df.index, utc=True)
            return df

        # Download fresh data
        df = self._download_from_yf(symbol, interval, period)

        # Cache to CSV
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_file)

        return df
