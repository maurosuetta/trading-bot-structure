import yfinance as yf
import pandas as pd
from datahandler import Datahandler
from backtest_engine import BacktestEngine
from sma_strategy import SMACrossoverStrategy
from strategy import Strategy
from portfolio import Portfolio

def main():
    AAPL = "AAPL"
    #test for 1 month
    data_AAPL = Datahandler(start_date="2022-01-01", end_date="2022-02-01", asset_symbol=AAPL)
    data_AAPL.load_data(path="AAPL_testing2024")
    sma = SMACrossoverStrategy(AAPL, 2, 5)
    portfolio = Portfolio(100000)
    backtest = BacktestEngine(data_AAPL, sma, portfolio)
    backtest.run_backtest()
    backtest.get_results()
    portfolio.get_current_holdings()

if __name__ == "__main__":
    main()