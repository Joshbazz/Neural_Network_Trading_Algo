import pandas as pd
import datetime
import os
import ccxt
import dontshare_config as d
from math import ceil
import time

import dotenv

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
dotenv_path = os.path.join(project_dir, '.env')
dotenv.load_dotenv(dotenv_path)

symbol = 'BTC/USD'
timeframe = '6h'

def timeframe_to_sec(timeframe):
    if 'm' in timeframe:
        return int(''.join([char for char in timeframe if char.isnumeric()])) * 60
    elif 'h' in timeframe:
        return int(''.join([char for char in timeframe if char.isnumeric()])) * 60 * 60
    elif 'd' in timeframe:
        return int(''.join([char for char in timeframe if char.isnumeric()])) * 24 * 60 * 60

def get_historical_data(symbol, timeframe, start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    filename = f'{symbol[0:3]}-{timeframe}-{start_date.date()}-to-{end_date.date()}.csv'
    if os.path.exists(filename):
        return pd.read_csv(filename, index_col='datetime', parse_dates=True)

    coinbase = ccxt.coinbase({
        'apiKey': d.CB_Key,
        'secret': d.CB_Secret,
        'enableRateLimit': True,
    })

    granularity = timeframe_to_sec(timeframe)
    total_time = (end_date - start_date).total_seconds()
    run_times = ceil(total_time / (granularity * 200))

    dataframe = pd.DataFrame()
    current_date = end_date

    for i in range(run_times):
        since = max(current_date - datetime.timedelta(seconds=granularity * 200), start_date)
        since_timestamp = int(since.timestamp()) * 1000

        try:
            data = coinbase.fetch_ohlcv(symbol, timeframe, since=since_timestamp, limit=200)
            df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            if not df.empty:
                dataframe = pd.concat([df, dataframe])
            
            current_date = since
            
            if current_date <= start_date:
                break

            time.sleep(1)
        except ccxt.base.errors.RateLimitExceeded:
            print("Rate limit exceeded, sleeping for 10 seconds...")
            time.sleep(10)
            continue

    if dataframe.empty:
        print(f"No data available for the period {start_date} to {end_date}")
        return None

    dataframe = dataframe.set_index('datetime')
    dataframe = dataframe[["open", "high", "low", "close", "volume"]]
    
    # Filter the dataframe to include data from the closest available date after start_date
    dataframe = dataframe.loc[dataframe.index >= start_date]
    dataframe = dataframe.loc[:end_date]  # This should not raise an error even if end_date is after the last available date
    
    if dataframe.empty:
        print(f"No data available within the specified date range")
        return None

    dataframe.to_csv(filename)
    return dataframe

# Example usage:
start_date = '2024-01-01'
end_date = '2024-06-27'
result = get_historical_data(symbol, timeframe, start_date, end_date)
if result is not None:
    print(result.head())
    print(result.tail())
    print(f"Data shape: {result.shape}")
else:
    print("Failed to retrieve data")