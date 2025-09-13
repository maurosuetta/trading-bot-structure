import pandas as pd
import yfinance as yf
import os

class Datahandler:

    def __init__(self, start_date='str', end_date='str', asset_symbol='str'):
        self.asset_symbol = asset_symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = pd.DataFrame()


    def load_data(self, source='yahoo', path=None) -> pd.DataFrame:
        db_dir = "databases"
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        csv_path = os.path.join(db_dir, f"{path}.csv") if path else None

        if source == "yahoo":
            print(f"Loading data for {self.asset_symbol} from {self.start_date} to {self.end_date}")
            self.data = yf.download(
                tickers=self.asset_symbol,
                start=self.start_date,
                end=self.end_date,
                multi_level_index=False)
            
            if self.data.empty:
                print("No data found for the specified asset or data range")
                # self.data.columns = self.data.droplevel(1)
            print(self.data.head())
            if csv_path:
                self.data.to_csv(csv_path)
                print(f"Data saved to {csv_path}.")
            else:
                print("Warning: No file name provided. Data not saved to CSV.")
        elif source == 'csv':
            if csv_path:
                try:
                    self.data = pd.read_csv(csv_path, skiprows=2, index_col='Date', parse_dates=True)
                    print(f"Data loaded from {csv_path}.")
                except FileNotFoundError:
                    print(f"Error: CSV file not found at {csv_path}.")
                except pd.errors.ParserError:
                    # If skipping rows fails, try normal loading
                    self.data = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
                    print(f"Data loaded from {csv_path} (no skipped rows).")
        
            else:
                print("Error: File name must be provided for 'csv' data source.")
        else:
            print("Error: Unsupported data source. Use 'yahoo' or 'csv'.")

        #IMPROVING AREA: DOING ERROR HANDLING FOR DATA LIMITATIONS AND DOING ALERTS

    def get_latest_data(self, n=1):
        if not self.data.empty:
            return self.data.tail(n)
        return pd.DataFrame()
    
    def head(self, n=1):
        if not self.data.empty:
            return self.data.head(n)
        return pd.DataFrame()
    
    def get_all_data(self):
        return self.data
    