import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

def plot_sma_crossover(asset_symbol, start_date, end_date, short_window=20, long_window=50):
    """
    Plots the closing price of an asset along with its short and long Simple Moving Averages.
    This visualization helps to understand the SMA crossover strategy.

    Args:
        asset_symbol (str): The symbol of the financial asset (e.g., 'GOOGL').
        start_date (str): The start date for the data.
        end_date (str): The end date for the data.
        short_window (int): The period for the short-term SMA.
        long_window (int): The period for the long-term SMA.
    """
    print(f"Downloading data for {asset_symbol} from {start_date} to {end_date}...")
    try:
        data = yf.download(asset_symbol, start=start_date, end=end_date)
        if data.empty:
            print("Failed to download data. Please check the asset symbol and dates.")
            return
    except Exception as e:
        print(f"An error occurred while downloading data: {e}")
        return

    # Calculate the short and long Simple Moving Averages
    data['short_sma'] = data['Close'].rolling(window=short_window).mean()
    data['long_sma'] = data['Close'].rolling(window=long_window).mean()
    for i in data:
        print(data[i])
    # Drop any rows with NaN values (which are the initial rows where SMA can't be calculated)
    data.dropna(inplace=True)

    # Plot the results
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.plot(data.index, data['short_sma'], label=f'SMA {short_window}', color='orange', linestyle='--')
    plt.plot(data.index, data['long_sma'], label=f'SMA {long_window}', color='green', linestyle='--')
    
    # Add title and labels
    plt.title(f'{asset_symbol} SMA Crossover Strategy Visualization', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # Define parameters for the plot
    ASSET_SYMBOL = 'GOOGL'
    START_DATE = '2022-01-01'
    END_DATE = '2022-02-01'
    SHORT_WINDOW = 2
    LONG_WINDOW = 5
    
    # Run the plotting function
    plot_sma_crossover(ASSET_SYMBOL, START_DATE, END_DATE, SHORT_WINDOW, LONG_WINDOW)
