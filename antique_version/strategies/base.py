"""
base.py — Abstract base class for trading strategies.

Responsibilities:
- Define interface for all strategies.
- Enforce methods for signal generation.
- Ensure consistency when integrating with backtest engine.
"""

from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    Each strategy must implement `generate_signals`.
    """

    def __init__(self, instrument: str, params: dict = None):
        """
        Initialize strategy.

        Args:
            instrument: Ticker symbol (e.g. 'TSLA', 'XRP-USD').
            params: Dict of parameters (e.g. moving average window lengths).
        """
        self.instrument = instrument
        self.params = params if params is not None else {}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on price data.

        Args:
            data: DataFrame containing price data with at least 'Close' column.

        Returns:
            pd.Series of signals (1 = long, -1 = short, 0 = neutral).
        """
        pass
