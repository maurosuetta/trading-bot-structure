import pandas as pd
from portfolio import Portfolio
from datahandler import Datahandler
from strategy import Strategy
from sma_strategy import SMACrossoverStrategy

class BacktestEngine:
    """
    Orchestrates the backtesting process by iterating through the data,
    generating signals, and executing trades.
    """
    def __init__(self, data_handler: Datahandler, strategy: Strategy, portfolio: Portfolio):
        """
        Initializes the backtest engine with the core components.

        Args:
            data_handler (DataHandler): An instance of the DataHandler class.
            strategy (Strategy): An instance of a Strategy subclass.
            portfolio (Portfolio): An instance of the Portfolio class.
        """
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        self.transactions = None
        self.equity_curve = None

    def run_backtest(self):
        """
        Runs the backtest simulation.
        
        The process involves:
        1. Getting all historical data from the DataHandler.
        2. Iterating through the data, one timestamp at a time.
        3. For each timestamp, the strategy generates a signal based on the data up to that point.
        4. The portfolio handles the signal and executes a trade if necessary.
        5. The portfolio's equity is updated at each step.
        """
        print("Starting backtest...")
        
        all_data = self.data_handler.get_all_data()
        if all_data.empty:
            print("Backtest cannot run. No data loaded.")
            return


        #AREA IMPROVEMENT MAKE A MORE EFFICIENT ITERATOR AND DATA ANALYSIS
        for i in range(len(all_data)):
            # Get the data available up to the current timestamp
            current_data = all_data.iloc[:i+1]
            current_timestamp = all_data.index[i]
            #print(current_data, current_timestamp)
            
            current_price = all_data['Close'].iloc[i]
            #print(current_price)
            current_prices = {self.strategy.asset_symbol: current_price}

            signal = self.strategy.generate_signals(current_data)

            #line calling portfolio function to iterate through trades and see if TP o SL activated and close them
            #deleting them from trades list and adding it as transaction
            
            self.portfolio.check_TP_SL(current_prices=current_prices, timestamp=current_timestamp)

            if signal != 'HOLD':
                self.portfolio.handle_signal(signal, current_timestamp, self.strategy.asset_symbol, current_price, current_prices)
            else:
                self.portfolio.calculate_equity(current_prices, current_timestamp)


        print("Backtest finished.")
        
        self.transactions, self.equity_curve = self.portfolio.get_results()

    def get_results(self):
        """
        Returns the final results of the backtest.
        """
        if self.transactions is None or self.equity_curve is None:
            print("Run the backtest first to get results.")
            return None, None
        
        # Calculate final metrics here (e.g., total return, drawdown)
        total_return = (self.equity_curve.iloc[-1] - self.equity_curve.iloc[0]) / self.equity_curve.iloc[0]
        
        print("\n--- Backtest Results ---")
        print(f"Final Equity: ${self.equity_curve.iloc[-1]:.2f}")
        print(f"Total Return: {total_return * 100:.2f}%")
        print(f"Number of Trades: {len(self.transactions)}")
        
        return self.transactions, self.equity_curve
