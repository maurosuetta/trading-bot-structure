"""
settings.py — Global configuration for the trading-bot-structure project.

This module centralizes:
- Symbol universe (intraday-friendly Yahoo Finance tickers)
- Data frequency and Yahoo constraints
- Paths (raw/processed data, logs, reports)
- Risk management defaults (position sizing, costs, SL/TP)
- Backtest defaults (sessions, timezones)
- Small helper functions (directory creation, interval/period sanity helpers)

Everything here is intentionally explicit and documented, so other modules
(datafeed/loader.py, backtest/engine.py, etc.) can import clean settings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, Optional
import zoneinfo


# =============================================================================
# Project Paths
# =============================================================================

# Detect project root as the folder that contains this file's parent /config
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

LOGS_DIR: Path = PROJECT_ROOT / "logs"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
VIS_DIR: Path = PROJECT_ROOT / "visualization"

# Ensure the directory tree exists at import time (safe idempotent mkdirs).
for _p in (DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR, REPORTS_DIR, VIS_DIR):
    _p.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Time & Sessions
# =============================================================================

# We will store/standardize times in UTC inside dataframes, and only localize
# for display or session-filtering as needed.
UTC_TZ = zoneinfo.ZoneInfo("UTC")
LOCAL_TZ = zoneinfo.ZoneInfo("Europe/Madrid")

# Market profiles define regular trading hours to optionally filter intraday bars.
# - US equities (SPY, TSLA): 09:30–16:00 America/New_York
# - Crypto & FX: 24h (no session filter by default)
# You can enable/disable session filtering per instrument in INSTRUMENTS below.
AMERICA_NEW_YORK = zoneinfo.ZoneInfo("America/New_York")

MARKET_PROFILES: Dict[str, dict] = {
    "US_EQUITY": {
        "timezone": AMERICA_NEW_YORK,
        "session_start": (9, 30),   # 09:30 ET
        "session_end": (16, 0),     # 16:00 ET
        "apply_session_filter": True,
    },
    "CRYPTO_24_7": {
        "timezone": UTC_TZ,         # effectively 24/7; timezone irrelevant
        "session_start": (0, 0),
        "session_end": (23, 59),
        "apply_session_filter": False,
    },
    "FX_24_5": {
        "timezone": UTC_TZ,         # near 24/5; we treat as 24h continuous for simplicity
        "session_start": (0, 0),
        "session_end": (23, 59),
        "apply_session_filter": False,
    },
}


# =============================================================================
# Universe (your 4 instruments)
# =============================================================================
# 1) XRP-USD (crypto), 2) SPY (ETF), 3) TSLA (stock), 4) EURUSD=X (FX, recommended for diversification)
# All are widely followed, highly liquid, and have intraday data on Yahoo Finance.

INSTRUMENTS: Dict[str, dict] = {
    "XRP-USD": {
        "symbol": "XRP-USD",
        "asset_class": "CRYPTO",
        "market_profile": "CRYPTO_24_7",
        "currency": "USD",
    },
    "SPY": {
        "symbol": "SPY",
        "asset_class": "EQUITY_ETF",
        "market_profile": "US_EQUITY",
        "currency": "USD",
    },
    "TSLA": {
        "symbol": "TSLA",
        "asset_class": "EQUITY_SINGLE",
        "market_profile": "US_EQUITY",
        "currency": "USD",
    },
    "EURUSD=X": {
        "symbol": "EURUSD=X",
        "asset_class": "FX",
        "market_profile": "FX_24_5",
        "currency": "USD",
    },
}

DEFAULT_UNIVERSE = list(INSTRUMENTS.keys())


# =============================================================================
# Yahoo Finance Intraday Constraints & Defaults
# =============================================================================
# Yahoo Finance enforces max period length per interval.
# Common intraday intervals and max periods:
# - "1m": period ≤ "7d"
# - "2m"/"5m": period ≤ "60d"
# - "15m"/"30m"/"60m"/"90m": period ≤ "730d" (approx 2 years)
# - "1h" is an alias some wrappers accept; prefer "60m" for yfinance.
#
# We default to 5-minute bars for a good balance of signal/noise and history length.

DEFAULT_INTERVAL: str = "5m"
DEFAULT_PERIOD: str = "60d"  # max for 5m on Yahoo
# If you change DEFAULT_INTERVAL, adjust DEFAULT_PERIOD accordingly.

# Safety map to help other modules request a valid (interval, max_period) pair.
YF_INTERVAL_LIMITS: Dict[str, str] = {
    "1m": "7d",
    "2m": "60d",
    "5m": "60d",
    "15m": "730d",
    "30m": "730d",
    "60m": "730d",
    "90m": "730d",
}


# =============================================================================
# Risk Management Defaults
# =============================================================================

@dataclass(frozen=True)
class Costs:
    """Transaction cost and slippage assumptions expressed in basis points (bps)."""
    commission_bps: float = 1.0      # 1 bp = 0.01%
    slippage_bps: float = 2.0        # round-trip slippage assumption


@dataclass(frozen=True)
class PositionSizing:
    """
    Simple sizing policy used by the backtest engine.
    - fixed_fraction: fraction of current equity to allocate per signal (0..1)
    - max_positions: optional cap on concurrent open positions
    """
    fixed_fraction: float = 0.25
    max_positions: Optional[int] = 1


@dataclass(frozen=True)
class RiskLimits:
    """Stop-loss and take-profit as fractional returns from entry price."""
    stop_loss_pct: float = 0.02      # 2%
    take_profit_pct: float = 0.04    # 4%


INITIAL_CAPITAL: float = 10_000.00
COSTS = Costs()
SIZING = PositionSizing()
RISK = RiskLimits()


# =============================================================================
# Backtest & Optimization Defaults
# =============================================================================

# Sampling calendar filter: if True, US equities get session filtering (RTH).
APPLY_SESSION_FILTER: bool = True

# Benchmark for performance comparison (e.g., SPY for US risk assets).
BENCHMARK_SYMBOL: str = "SPY"

# Optimization search grids for SMA crossover (short < long).
SMA_SHORT_GRID = [5, 10, 15, 20]
SMA_LONG_GRID = [30, 50, 100, 150, 200]

# Random seeds for reproducibility in any stochastic components.
PY_RANDOM_SEED: int = 42
NP_RANDOM_SEED: int = 42


# =============================================================================
# Helper Functions
# =============================================================================

def yf_max_period_for_interval(interval: str) -> str:
    """
    Return a safe Yahoo Finance max period for a given intraday interval.
    Falls back to DEFAULT_PERIOD if the interval is unknown.
    """
    return YF_INTERVAL_LIMITS.get(interval, DEFAULT_PERIOD)


def get_universe() -> Dict[str, dict]:
    """Return the instrument dictionary (mutable copy not needed for read-only use)."""
    return INSTRUMENTS


def market_profile_for(symbol: str) -> dict:
    """
    Return the market profile dict for a given symbol based on INSTRUMENTS mapping.
    Raises KeyError if symbol does not exist or profile missing.
    """
    meta = INSTRUMENTS[symbol]
    profile_name = meta["market_profile"]
    return MARKET_PROFILES[profile_name]


def ensure_dirs() -> None:
    """
    Ensure required project directories exist (idempotent).
    Useful if downstream scripts run in isolation.
    """
    for _p in (DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR, REPORTS_DIR, VIS_DIR):
        _p.mkdir(parents=True, exist_ok=True)


def default_download_params() -> Tuple[str, str]:
    """
    Convenience for modules that want the current (interval, period) pair
    respecting Yahoo constraints.
    """
    return DEFAULT_INTERVAL, yf_max_period_for_interval(DEFAULT_INTERVAL)


def path_for_raw_csv(symbol: str, interval: str) -> Path:
    """
    Build a deterministic filename for raw downloads, e.g.:
    data/raw/SPY_5m.csv
    """
    safe_symbol = symbol.replace("=", "-").replace("/", "-")
    return RAW_DATA_DIR / f"{safe_symbol}_{interval}.csv"


def path_for_processed_csv(symbol: str, interval: str) -> Path:
    """
    Build a deterministic filename for processed datasets, e.g.:
    data/processed/SPY_5m.parquet OR csv
    Here we keep CSV for simplicity and interoperability.
    """
    safe_symbol = symbol.replace("=", "-").replace("/", "-")
    return PROCESSED_DATA_DIR / f"{safe_symbol}_{interval}.csv"
