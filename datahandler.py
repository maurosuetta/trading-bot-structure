import pandas as pd
import yfinance as yf

class Datahandler:

    def __init__(self, start_date='str', end_date='str', asset_symbol='str'):
        self.asset_symbol = asset_symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = pd.DataFrame()


    def load_data(self, source='yahoo', path=None) -> pd.DataFrame:
        if source=="yahoo":
            print(f"Loading data for {self.asset_symbol} from {self.start_date} to {self.end_date}")
            self.data = yf.download(tickers= self.asset_symbol, start=self.start_date, end=self.end_date)
            if self.data.empty:
                print("No data found for the specified asset or data range")
        elif source == 'csv':
            if path:
                try:
                    self.data = pd.read_csv(path, index_col='Date', parse_dates=True)
                    print(f"Data loaded from {path}.")
                except FileNotFoundError:
                    print(f"Error: CSV file not found at {path}.")
            else:
                print("Error: Path must be provided for 'csv' data source.")
        else:
            print("Error: Unsupported data source. Use 'yahoo' or 'csv'.")

        #IMPROVING AREA: DOING ERROR HANDLING FOR DATA LIMITATIONS AND DOING ALERTS

    def get_latest_data(self, n=1):
        if not self.data.empty:
            return self.data.tail(n)
        return pd.DataFrame()
    
    def get_all_data(self):
        return self.data
