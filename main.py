import yfinance as yf
import pandas as pd
from datahandler import Datahandler
from backtest_engine import BacktestEngine
from sma_strategy import SMACrossoverStrategy
from strategy import Strategy
from portfolio import Portfolio
from performance_analyzer import PerformanceAnalyzer

def main():
    AAPL = "AAPL"
    #test for 1 month
    data_AAPL = Datahandler(start_date="2022-01-01", end_date="2025-01-01", asset_symbol=AAPL)
    data_AAPL.load_data(path="AAPL_testing2024")
    sma = SMACrossoverStrategy(AAPL, 20, 50)
    portfolio = Portfolio(100000)
    backtest = BacktestEngine(data_AAPL, sma, portfolio)
    backtest.run_backtest()
    backtest.get_results()
    performance = PerformanceAnalyzer(portfolio=portfolio, data=data_AAPL.get_all_data())
    #print(portfolio.equity_curve)
    portfolio.get_current_holdings()
    portfolio.get_results()
    performance.calculate_metrics()
    metrics = performance.calculate_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    performance.plot_results()

if __name__ == "__main__":
    main()