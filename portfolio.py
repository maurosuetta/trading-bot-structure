import pandas as pd
from transactions import Transaction
from trade import Trade

class Portfolio:
    """
    Manages the capital, positions, and transaction history for the backtest.
    """
    def __init__(self, initial_capital=100000.0):
        """
        Initializes the portfolio with a starting capital.

        Args:
            initial_capital (float): The starting amount of cash in the portfolio.
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  #Dictionary to hold the quantity of each asset
        self.transactions = []  # List to record all transaction details
        self.trades = []
        self.equity_curve = pd.Series(dtype=float) #List to track portfolio value over time

    def handle_signal(self, signal, timestamp, asset_symbol, price, all_prices):
        """
        Processes a trading signal and executes the corresponding order.

        Args:
            signal (str): The trading signal ('LONG', 'SHORT', 'HOLD').
            timestamp (datetime): The timestamp of the signal.
            asset_symbol (str): The symbol of the asset.
            price (float): The current price of the asset for the transaction.
            all_prices (dict): A dictionary of current prices for all relevant assets.
        """
        trade_quantity = 150 #SIMPLIFIED

        if signal == 'LONG':
            long_trade = Trade(
                timestamp=timestamp,
                type='LONG',
                asset=asset_symbol,
                quantity=trade_quantity,
                entry_price=price)
            
            cost = long_trade.cost_trade()

            if self.current_capital >= cost:
                long_trade.open_trade()
                quantity = long_trade.quantity

                #register cost in current capital and update positions
                self.current_capital -= cost
                self.positions[asset_symbol] = self.positions.get(asset_symbol, 0) + quantity

                self._record_transaction(long_trade)
                print(f"[{timestamp}] Executed LONG order for {quantity} units of {asset_symbol} at {price:.2f}.")
            else:
                print(f"[{timestamp}] Insufficient funds to go long on {quantity} units of {asset_symbol}.")

        elif signal == 'SHORT':
            short_trade = Trade(
                timestamp=timestamp,
                type='SHORT',
                asset=asset_symbol,
                quantity=trade_quantity,
                entry_price=price)
            
            revenue = short_trade.cost_trade()  # Assuming cost_trade returns the proceeds for SHORT

            short_trade.open_trade()
            quantity = short_trade.quantity

            # Register revenue in current capital and update positions
            self.current_capital += revenue
            self.positions[asset_symbol] = self.positions.get(asset_symbol, 0) - quantity

            self._record_transaction(short_trade)
            print(f"[{timestamp}] Executed SHORT order for {quantity} units of {asset_symbol} at {price:.2f}.")
        self.calculate_equity(all_prices, timestamp)
    
    def _record_transaction(self, trade=Trade):
        """
        Records the details of a transaction in the transactions list.
        This is a helper method, not meant to be called directly from outside the class.
        """
        # Extract transaction details from the Trade object
        timestamp = trade.timestamp
        type = trade.type
        asset_symbol = trade.asset
        quantity = trade.quantity
        price = trade.entry_price

        new_transaction = Transaction(
            timestamp=timestamp,
            type=type,
            asset=asset_symbol,
            quantity=quantity,
            price=price)

        self.transactions.append(new_transaction)

    def calculate_equity(self, current_prices, timestamp):
        """
        Calculates the current total value of the portfolio.

        Args:
            current_prices (dict): A dictionary mapping asset symbols to their latest prices.
        """
        positions_value = 0
        for asset, qty in self.positions.items():
            if asset in current_prices:
                positions_value += qty * current_prices[asset]
        
        # Total equity is the sum of current capital and positions value
        current_equity = self.current_capital + positions_value
        self.equity_curve.at[timestamp] = current_equity

    def get_current_holdings(self):
        """
        Returns the current positions held by the portfolio.
        """
        return self.positions

    def get_results(self):
        """
        Returns the final transaction and equity data for analysis.
        """
        return pd.DataFrame(self.transactions), self.equity_curve
