# strategies/sma_crossover.py
"""
SMA Crossover Strategy (Momentum).

Corrección: usar columna 'close' en minúsculas para compatibilidad con DataLoader.
"""

import pandas as pd
from strategies.base import Strategy


class SMACrossoverStrategy(Strategy):
    def __init__(self, instrument: str, short_window: int = 10, long_window: int = 50):
        super().__init__(instrument, params={"short_window": short_window, "long_window": long_window})

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        short_window = self.params["short_window"]
        long_window = self.params["long_window"]

        short_ma = data["close"].rolling(window=short_window, min_periods=1).mean()
        long_ma = data["close"].rolling(window=long_window, min_periods=1).mean()

        signals = pd.Series(0, index=data.index, dtype="int8")
        signals[short_ma > long_ma] = 1
        signals[short_ma < long_ma] = -1
        return signals
