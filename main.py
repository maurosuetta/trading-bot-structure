import yfinance as yf
import pandas as pd
from Datahandler import Datahandler
from backtest_engine import BacktestEngine
from sma_strategy import SMACrossoverStrategy
from ema_strategy import EMACrossoverStrategy
from strategy import Strategy
from portfolio import Portfolio
from performance_analyzer import PerformanceAnalyzer
from MasterDatahandler import MasterDatahandler

def main():
    assets = ["AAPL", "TSLA", "NVDA"]
    data_handler = MasterDatahandler(asset_symbols=assets, start_date="2022-01-01", end_date="2025-01-01")
    data_handler.load_all_data(source='yahoo')  # or source='yahoo' if downloading
    
    print("\nSTARTING OLD BACKTEST")
    AAPL = "SPY"
    #test for 1 month
    data_AAPL = Datahandler(start_date="2022-01-01", end_date="2025-01-01", asset_symbol=AAPL)
    data_AAPL.load_data(path="AAPL_testing2024")

    # Access master DataFrame
    master_df = data_handler.master_df
    AAPL = Datahandler
    #sma = SMACrossoverStrategy(AAPL, 4, 10)
    ema = EMACrossoverStrategy(AAPL, 4, 10)
    portfolio = Portfolio(100000)
    backtest = BacktestEngine(data_AAPL, ema, portfolio)
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