import pandas as pd
import os
from keras.models import load_model
from sklearn.preprocessing import RobustScaler
import datetime

def generate_signal(model_path, data_path, test_size, window_size=40):
    # Load the saved model
    model = load_model(model_path)

    # Load new data for backtesting
    new_data = pd.read_csv(data_path, parse_dates=True, index_col='Date')

    # Calculate the index for splitting into 75% training and 25% testing
    split_index = int(len(new_data) * (1 - test_size))

    # Split the data into training and testing sets
    data = new_data.iloc[split_index:]
    data = data.dropna()
    prices = data['Close'].copy()

    print(type(prices))

    # Preprocess the new data using the same window size as during training
    def create_backtest_data(prices, window_size):
        data = []
        for i in range(len(prices) - window_size):
            X_new = prices.iloc[i:i + window_size]
            y = prices.iloc[i + window_size]
            data.append(list(X_new) + [y])
        columns = [f't-{i}' for i in range(window_size, 0, -1)] + ['t']
        return pd.DataFrame(data, columns=columns)

    dataset = create_backtest_data(prices, window_size)

    # Assign target and feature sets
    X = dataset.iloc[:, :-1]
    y = dataset.iloc[:, -1].values.reshape(-1, 1)

    # Normalize features (using the same scaler as during training)
    scaler = RobustScaler()
    scaler.fit(X)
    X_scaled = scaler.transform(X)

    scaler_y = RobustScaler()
    scaler_y.fit(y)
    y_scaled = scaler_y.transform(y)

    # Predict with the model
    predictions_scaled = model.predict(X_scaled)

    # Inverse transform predictions to get unscaled prices
    predictions = scaler_y.inverse_transform(predictions_scaled).flatten()

    # Implement trading strategy based on unscaled predictions
    positions = []
    current_position = 0

    for i in range(len(predictions)):
        # Buy if predicted close for the next day is higher than current day's open
        if predictions[i] > data['Open'].iloc[i + window_size] and current_position <= 0:
            positions.append(1)  # 1 indicates BUY
            current_position += 1
        # Sell if predicted close for the next day is lower than current day's open
        elif predictions[i] < data['Open'].iloc[i + window_size]:
            if current_position > 0:
                positions.append(-1)  # -1 indicates SELL
                current_position = 0
            else:
                positions.append(0)  # 0 indicates no action
        else:
            positions.append(0)  # No action if none of the conditions are met

    # Handle last day: sell remaining position if any
    if current_position > 0:
        positions.append(-1)

    # Adjust data to match the length of positions
    data_adjusted = data.iloc[window_size:].copy()

    # Ensure positions length matches data_adjusted length
    positions = positions[:len(data_adjusted)]

    # Add positions to the adjusted DataFrame
    data_adjusted['Signal'] = positions

    # Get the current timestamp and format it
    current_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    # Define the directory and ensure it exists
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    os.makedirs(data_dir, exist_ok=True)

    # Define the full path for the new CSV file
    csv_path = os.path.join(data_dir, f'{current_timestamp}_new_data_with_positions.csv')

    # Save new_data with positions
    data_adjusted.to_csv(csv_path, index=True)

    # # Save new_data with positions
    # data_adjusted.to_csv(f'neural_network_trading_algo/data/{current_timestamp}_new_data_with_positions.csv', index=True)

    print(f"Data shape: {data_adjusted.shape}")
    print(f"Positions length: {len(positions)}")

    data_string = f'data/{current_timestamp}_new_data_with_positions.csv'

    return csv_path

    # Define the directory and ensure it exists
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    os.makedirs(data_dir, exist_ok=True)

    # Define the full path for the new CSV file
    csv_path = os.path.join(data_dir, f'{current_timestamp}_new_data_with_positions.csv')

    # Save new_data with positions
    data_adjusted.to_csv(csv_path, index=True)