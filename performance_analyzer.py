import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import mplfinance as mpf
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
        transactions_data, equity_data = self.portfolio.get_results()
        self.transactions = transactions_data
        self.transactions.set_index('timestamp', inplace=True)
        self.equity_curve = equity_data
        self.data = data

        # Ensure the data has a DatetimeIndex for mplfinance
        if not isinstance(self.data.index, pd.DatetimeIndex):
            self.data.index = pd.to_datetime(self.data.index)
        
        # # Ensure the transactions DataFrame has a DatetimeIndex
        # if not self.transactions.empty:
        #     self.transactions.index = pd.to_datetime(self.transactions['timestamp'])

        print("\nDebug info for PerformanceAnalyzer:")
        print(f"Equity curve received: \n{self.equity_curve.head()}")
        print(f"Transactions received: \n{self.transactions.head()}\n")
    
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
        risk_free_win = 0.04 * initial_capital
        
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
        Generates two improved plots: an equity curve plot and a candlestick chart with trade markers.
        """
        if self.equity_curve.empty or self.data.empty:
            print("No data to plot.")
            return
        
        # --- Plot 1: Equity Curve using Seaborn ---
        plt.figure(figsize=(14, 5))
        sns.set_style("whitegrid")
        sns.lineplot(x=self.data.index, y=self.equity_curve, color='black', linewidth=1)
        plt.title('Portfolio Equity Curve', fontsize=16)
        plt.ylabel('Portfolio Equity (USD)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
                
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=31))  # Change interval as needed
        plt.show()
        # Show more x-axis labels (e.g., every 7 days)
        # --- Plot 2: Candlestick Chart with mplfinance ---
        add_plots = []
        if not self.transactions.empty:
            long_entries = self.transactions[self.transactions['type'] == 'LONG']
            short_entries = self.transactions[self.transactions['type'] == 'SHORT']

            long_markers = [np.nan] * len(self.data)
            for i in range(len(self.data.index)):
                if self.data.index[i] in long_entries.index:
                    long_markers[i] = self.data['Low'].iloc[i] * 0.99

            short_markers = [np.nan] * len(self.data)
            for i in range(len(self.data.index)):
                if self.data.index[i] in short_entries.index:
                    short_markers[i] = self.data['High'].iloc[i] * 1.01

            add_plots.append(mpf.make_addplot(long_markers, type='scatter', marker='^', markersize=100, color='green', label='LONG Entry'))
            add_plots.append(mpf.make_addplot(short_markers, type='scatter', marker='v', markersize=100, color='red', label='SHORT Entry'))

        # This will open a new window for the candlestick chart
        mpf.plot(
            self.data,
            type='line',
            mav=(4, 10),
            style='nightclouds',
            title='Asset Price with Trades',
            addplot=add_plots,
            figsize=(16, 9),
            tight_layout=True,
            show_nontrading=True
        )