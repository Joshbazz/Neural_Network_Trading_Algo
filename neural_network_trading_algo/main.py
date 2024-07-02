from modeling.dnn import StockPricePrediction
from sklearn.model_selection import train_test_split
from modeling.generate_signals import generate_signal
from visualization.model_plot import save_and_visualize_model
from backtester.backtester_live import *
from data.fetch_data import fetch_and_save_data

# Example usage
# Define the data path
ticker = '^STI'  # Example ticker
start_date = '2010-01-01'
end_date = '2017-01-03'
file_path = f'data/{ticker}_data_end_{end_date}_start_{start_date}.csv'


fetch_and_save_data(ticker, start_date, end_date, file_path)


# data_string = 'data/old_ohlcv/BTC-6h-2023-01-01-to-2024-06-27.csv'

# Create an instance of the class
stock_predictor = StockPricePrediction(file_path)

# set the test_size. if test size is .25, then 75% of data will be used to train
test_size = 0.25

# Load and preprocess data
# train_percent [0,1] => determines percent of data that goes to training
data, data_create = stock_predictor.load_and_preprocess_data()

# Create dataset
dataset = stock_predictor.create_dataset(data_create)
X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

# retain X_test slice of original dataframe
backtest_data = data.iloc[-len(X_test):].copy()

# Normalize data
X_train_scaled, y_train_scaled = stock_predictor.normalize_data(X_train, y_train)
X_test_scaled, y_test_scaled = stock_predictor.scaler.transform(X_test), stock_predictor.y_scaler.transform(y_test.values.reshape(-1, 1))

# set the amount of epochs. default is 50
epochs = 50

# Build and train model
stock_predictor.build_model()
stock_predictor.train_model(X_train_scaled, y_train_scaled, epochs=epochs)

# # Evaluate model
loss, predictions = stock_predictor.evaluate_model(X_test_scaled, y_test_scaled)

# Inverse transform predictions and actual values
y_test_inv, predictions_inv = stock_predictor.inverse_transform(y_test_scaled, predictions)

# Save the model
model_path = stock_predictor.save_model(epochs=epochs)

#NOTE uncomment when graphviz is installed
# save_and_visualize_model(model_path)

# Generate Signals csv
signals_string = generate_signal(model_path, file_path, test_size)

# Call the function with the path to your CSV file
run_backtest(signals_string)