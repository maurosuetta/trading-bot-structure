"""
main.py — Main entry point for trading bot.

Responsibilities:
- Load configuration and tickers.
- Download historical/intraday data.
- Run strategies and backtesting engine.
- Show performance metrics and plots.
"""

import yfinance as yf
import pandas as pd
from strategies.sma_crossover import SMACrossoverStrategy
from backtest.engine import BacktestEngine
from antique_version.plots import plot_equity_curve, plot_cumulative_pnl, plot_signals
from visualization.candles import plot_candles_with_indicators

def main():
    # --- CONFIG ---
    tickers = ["SPY"]  # Example instruments
    short_window = 10
    long_window = 50
    size_per_trade = 1
    capital = 100000

    for ticker in tickers:
        print(f"Running backtest for {ticker}...")

        # --- DATA ---
        data = yf.download(ticker, period="5d", interval="15m", auto_adjust=False)
        print("Columns:\n")
        print(data.head())
        print(data.tail(10))        
        # Normalizar columnas
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [''.join(col).strip() for col in data.columns]

        if "Close" not in data.columns:
            close_col = [c for c in data.columns if "Close" in str(c)][0]
            data.rename(columns={close_col: "Close"}, inplace=True)

        if data.empty:
            print(f"No data for {ticker}, skipping.")
            continue

        # --- STRATEGY ---
        strategy = SMACrossoverStrategy(ticker, short_window=short_window, long_window=long_window)

        # --- BACKTEST ---
        engine = BacktestEngine(strategy, initial_capital=capital)
        engine.run(data, size_per_trade=size_per_trade)
        performance = engine.get_performance()
        print(f"Performance for {ticker}:")
        for k, v in performance.items():
            print(f"  {k}: {v:.4f}")
        """
        # --- PLOTS ---
        print(data.columns)
        plot_equity_curve(engine.equity_curve, title=f"{ticker} Equity Curve")
        plot_cumulative_pnl(engine.portfolio.trades_closed, title=f"{ticker} Cumulative PnL")
        plot_signals(data, strategy.generate_signals(data), title=f"{ticker} Trading Signals")
        plot_candles_with_indicators(data, signals=strategy.generate_signals(data), mav=[short_window, long_window], title=f"{ticker} Candlestick Chart")
        """
if __name__ == "__main__":
    main()