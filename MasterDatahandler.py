from Datahandler import Datahandler
import pandas as pd

class MasterDatahandler:
    def __init__(self, asset_symbols, start_date, end_date):
        self.asset_symbols = asset_symbols
        self.start_date = start_date
        self.end_date = end_date
        self.handlers = {symbol: Datahandler(start_date, end_date, symbol) for symbol in asset_symbols}
        self.master_df = pd.DataFrame()

    def load_all_data(self, source='yahoo'):
        for symbol, handler in self.handlers.items():
            handler.load_data(source=source)
        self.create_master_dataframe()

    def create_master_dataframe(self):
        dfs = []
        for symbol, handler in self.handlers.items():
            df = handler.get_all_data()[['Close']].rename(columns={'Close': f'{symbol}_Close'})
            dfs.append(df)
        self.master_df = pd.concat(dfs, axis=1)
        print("\n-- PRICE ASSETS DATABASE --\n")
        print(self.master_df.head(), "\n")