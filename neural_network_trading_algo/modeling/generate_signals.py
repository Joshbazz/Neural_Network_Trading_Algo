import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# Load the saved model
model = load_model('stock_price_prediction_model.keras')

# Load new data for backtesting (example: new dataset with unseen data)
new_data = pd.read_csv('cleaned_BTC-15m-2015-07-20-to-2024-06-27.csv', parse_dates=True, index_col='datetime')

# Calculate the index for splitting into 75% training and 25% testing
split_index = int(len(new_data) * 0.75)

# Split the data into training and testing sets
data = new_data.iloc[split_index:]
data = data.dropna()
prices = data['close'].copy()

# Preprocess the new data using the same window size as during training
def create_backtest_data(prices, window_size):
    data = []
    for i in range(len(prices) - window_size):
        X_new = prices[i:i + window_size]
        y = prices[i + window_size]
        data.append(list(X_new) + [y])
    columns = [f't-{i}' for i in range(window_size, 0, -1)] + ['t']
    return pd.DataFrame(data, columns=columns)

window_size = 40
dataset = create_backtest_data(prices, window_size)

# assign target and feature sets
X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1].values.reshape(-1, 1)

# Normalize features (using the same scaler as during training)
scaler = MinMaxScaler()
scaler.fit(X)
X_scaled = scaler.transform(X)

scaler_y = MinMaxScaler()
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
    if predictions[i] > data['open'].iloc[i + window_size] and current_position <= 0:
        positions.append(1)  # 1 indicates BUY
        current_position += 1
    # Sell if predicted close for the next day is lower than current day's open
    elif predictions[i] < data['open'].iloc[i + window_size]:
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
data_adjusted['Position'] = positions

# Save new_data with positions
data_adjusted.to_csv('new_data_with_positions.csv', index=True)

print(f"Data shape: {data_adjusted.shape}")
print(f"Positions length: {len(positions)}")