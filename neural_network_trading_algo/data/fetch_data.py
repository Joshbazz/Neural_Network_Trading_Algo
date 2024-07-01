import os
import yfinance as yf
import pandas as pd

def fetch_and_save_data(ticker, start_date, end_date, file_path):
    """
    Fetches historical data for a given ticker and timeframe from Yahoo Finance and saves it to a CSV file.
    
    Parameters:
    - ticker: str, stock ticker symbol
    - start_date: str, start date in 'YYYY-MM-DD' format
    - end_date: str, end date in 'YYYY-MM-DD' format
    - file_path: str, path to save the CSV file
    
    Returns:
    - None
    """
    # Fetch the historical data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Ensure the directory exists before saving the file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the data to a CSV file
    data.to_csv(file_path)
    
    print(f"Data for {ticker} from {start_date} to {end_date} has been saved to {file_path}")

# # Example usage
# if __name__ == "__main__":
#     ticker = '^STI'  # Example ticker
#     start_date = '2010-01-01'
#     end_date = '2017-01-03'
#     file_path = f'{ticker}_data_end_{end_date}_start_{start_date}.csv'
    
#     fetch_and_save_data(ticker, start_date, end_date, file_path)
