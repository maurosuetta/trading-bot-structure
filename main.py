import yfinance as yf
import pandas as pd
from datahandler import Datahandler

def main():
    AAPL = "AAPL"
    data_AAPL = Datahandler(start_date="2022-01-01", end_date="2025-08-01", asset_symbol=AAPL)
    data_AAPL.load_data(path="AAPL_testing2024")

if __name__ == "__main__":
    main()