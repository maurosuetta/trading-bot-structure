import pandas as pd
from strategy import Strategy

class EMACrossoverStrategy(Strategy):
    """
    A strategy that generates signals based on an Exponential Moving Average (EMA) crossover.
    """
    def __init__(self, asset_symbol, short_window=2, long_window=5):
        super().__init__(asset_symbol)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data):
        """
        Generates a signal based on the crossover of two EMAs.

        A 'LONG' signal is generated when the short EMA crosses above the long EMA.
        A 'SHORT' signal is generated when the short EMA crosses below the long EMA.
        """
        if len(data) < self.long_window:
            return 'HOLD'

        # Calculate the short and long EMAs
        short_ema = data['Close'].ewm(span=self.short_window, adjust=False).mean()
        long_ema = data['Close'].ewm(span=self.long_window, adjust=False).mean()

        # Get the latest EMA values
        latest_short_ema = short_ema.iloc[-1]
        latest_long_ema = long_ema.iloc[-1]

        previous_short_ema = short_ema.iloc[-2]
        previous_long_ema = long_ema.iloc[-2]

        # Check for a crossover
        if previous_short_ema <= previous_long_ema and latest_short_ema > latest_long_ema:
            return 'LONG'
        elif previous_short_ema >= previous_long_ema and latest_short_ema < latest_long_ema:
            return 'SHORT'
        else:
            return 'HOLD'
