import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from portfolio import Portfolio

class PerformanceAnalyzer:
    """
    Calculates and visualizes the performance metrics of a trading backtest.
    """
    def __init__(self, portfolio, data):
        """
        Initializes the analyzer with a portfolio instance and historical data.

        Args:
            portfolio (Portfolio): The Portfolio instance after the backtest has run.
            data (pd.DataFrame): The full historical data used for the backtest.
        """
        self.portfolio = portfolio
        # Get results directly and handle potential empty data
        results = self.portfolio.get_results()
        self.transactions = results[0]
        self.equity_curve = results[1]
        self.data = data
        
        print("\nDebug info for PerformanceAnalyzer:")
        print(f"Equity curve received: {self.equity_curve.head()}")
        print(f"Transactions received: \n{self.transactions.head()}")
        
        # Ensure the equity curve is indexed by dates
        # if not self.equity_curve.empty:
        #     dates = pd.to_datetime(self.equity_curve.index)
        #     self.equity_curve.index = dates
        # print("After datetime")
        # print(self.equity_curve.head())

    def calculate_metrics(self):
        """
        Calculates key performance metrics of the backtest.

        Returns:
            dict: A dictionary containing the calculated metrics.
        """
        if self.equity_curve.empty or len(self.equity_curve) < 2:
            print("Not enough data to calculate metrics.")
            return {}

        initial_capital = self.portfolio.initial_capital
        final_equity = self.equity_curve.iloc[-1]
        
        # Total Return
        total_return = (final_equity - initial_capital) / initial_capital

        # Annualized Return (assuming data is daily)
        num_days = len(self.equity_curve)
        annualized_return = ((1 + total_return) ** (252 / num_days)) - 1 if num_days > 0 else 0

        # Drawdown and Max Drawdown
        equity_series = pd.Series(self.equity_curve)
        rolling_max = equity_series.cummax()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Use S&P 500 annualized return as risk-free rate (approx. 8% historically)
        risk_free_rate = 0.04 / 252  # daily risk-free rate

        # Sharpe Ratio calculation
        daily_returns = self.equity_curve.pct_change().dropna()
        excess_daily_returns = daily_returns - risk_free_rate
        sharpe_ratio = np.sqrt(252) * excess_daily_returns.mean() / excess_daily_returns.std() if excess_daily_returns.std() != 0 else 0
        risk_free_win = 0.04*100000
        return {
            "Initial Capital": initial_capital,
            "Final Equity": final_equity,
            "Total Return (%)": total_return * 100,
            "Annualized Return (%)": annualized_return * 100,
            "Max Drawdown (%)": max_drawdown * 100,
            "Sharpe Ratio": sharpe_ratio,
            "Risk free win": risk_free_win
        }

    def plot_results(self):
        """
        Generates two plots: the portfolio equity curve and the asset price with trade markers.
        """
        if self.equity_curve.empty or self.data.empty:
            print("No data to plot.")
            return

        # Create a figure with two subplots, arranged vertically
        fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [1, 2]})
        
        # --- Plot 1: Equity Curve ---
        ax1.plot(self.equity_curve.index, self.equity_curve, label='Equity Curve', color='purple', linewidth=2)
        ax1.set_title('Portfolio Equity Curve', fontsize=16)
        ax1.set_ylabel('Portfolio Equity (USD)', fontsize=12)
        ax1.grid(True)
        ax1.legend(loc='upper left')

        # --- Plot 2: Asset Price with Trade Markers ---
        ax2.plot(self.data.index, self.data['Close'], label='Close Price', color='blue')
        ax2.set_title('Price with Trades', fontsize=16)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Price (USD)', fontsize=12)
        ax2.grid(True)
        
        # Add transaction markers
        if not self.transactions.empty:
            long_entries = self.transactions[self.transactions['type'] == 'LONG']
            short_entries = self.transactions[self.transactions['type'] == 'SHORT']
            
            # Plot long entries as green upward triangles on the price chart
            ax2.plot(pd.to_datetime(long_entries['timestamp']), long_entries['price'], '^', markersize=10, color='green', label='LONG Entry', zorder=10)
            
            # Plot short entries as red downward triangles on the price chart
            ax2.plot(pd.to_datetime(short_entries['timestamp']), short_entries['price'], 'v', markersize=10, color='red', label='SHORT Entry', zorder=10)
        
        ax2.legend()
        plt.tight_layout()
        plt.show()
