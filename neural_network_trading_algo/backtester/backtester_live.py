import pandas as pd
from backtesting import Backtest, Strategy
    
class SignalStrategy(Strategy):
    def init(self):
        self.signal = self.data.Signal

    def next(self):
        current_signal = self.data.Signal[-1]
        current_date = self.data.index[-1]
        print(f"Date: {current_date}, Current position size: {self.position.size}, Signal: {current_signal}, Position: {self.position.is_long}")
        
        if current_signal == 1:
            print("Executing BUY order")
            self.buy(size=1)
        elif current_signal == -1 and self.position.is_long:
            print("Attempting to SELL entire position")
            try:
                self.position.close()  # This closes the entire position
                print("SELL order executed - entire position closed")
            except Exception as e:
                print(f"Error executing SELL order: {e}")
        elif current_signal == 0:
            print("No trade executed")
    
        
        # print(f"Current position size: {self.position.size}")

# load data
# dataframe = pd.read_csv('data/2024_06_29_17_13_04_new_data_with_positions.csv', index_col='datetime', parse_dates=True)
# data_string = 
def run_backtest(data_path, cash=1_000_000, commission=0.002, trade_on_close=True):
    # Load and preprocess the data
    dataframe = pd.read_csv(data_path, index_col='Date', parse_dates=True)
    dataframe = dataframe.sort_index()
    dataframe = dataframe.dropna()
    dataframe = dataframe.drop_duplicates()

    # Rename the columns to match the required format
    dataframe.columns = [column.capitalize() for column in dataframe.columns]

    # Initialize and run the backtest
    bt = Backtest(dataframe, SignalStrategy, cash=cash, commission=commission, trade_on_close=trade_on_close)
    stats = bt.run()

    # Print the statistics and plot the backtest results
    print(stats)
    bt.plot()