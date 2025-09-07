import pandas as pd
from strategy import Strategy

class SMACrossoverStrategy(Strategy):
    """
    A strategy that generates signals based on a Simple Moving Average (SMA) crossover.
    """
    def __init__(self, asset_symbol, short_window=2, long_window=5):
        super().__init__(asset_symbol)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data):
        """
        Generates a signal based on the crossover of two SMAs.
        
        A 'BUY' signal is generated when the short SMA crosses above the long SMA.
        A 'SELL' signal is generated when the short SMA crosses below the long SMA.
        """
        if len(data) < self.long_window:
            return 'HOLD'

        # Calculate the short and long SMAs
        short_sma = data['Close'].rolling(window=self.short_window).mean()
        print(short_sma)
        long_sma = data['Close'].rolling(window=self.long_window).mean()
        print(short_sma)
        # Get the latest SMA values
        latest_short_sma = short_sma.iloc[-1]
        print("iloc:", short_sma.iloc[-1])
        print(f"latest_short_sma = {latest_short_sma}")
        latest_long_sma = long_sma.iloc[-1]
        print(f"latest_long_sma = {latest_long_sma}")

        # Get the previous SMA values for comparison
        previous_short_sma = short_sma.iloc[-2]
        print(f"previous_short_sma = {previous_short_sma}")
        previous_long_sma = long_sma.iloc[-2]
        print(f"previous_long_sma = {previous_long_sma}")

        # Check for a crossover
        if previous_short_sma <= previous_long_sma and latest_short_sma > latest_long_sma:
            print("LONG!")
            return 'LONG'
        elif previous_short_sma >= previous_long_sma and latest_short_sma < latest_long_sma:
            print("SHORT!")
            return 'SHORT'
        else:
            print("hold...")
            return 'HOLD'