import datetime
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# Load and preprocess data
data = pd.read_csv('MERGED_BTC-15m-2015-07-20-to-2024-06-27.csv', parse_dates=True, index_col='datetime')

# Calculate the index for splitting into 75% training and 25% testing
# split_index is the index position of the end of the first 75% of the data
split_index = int(len(data) * 0.75)
# print(split_index)

# Split the data into training and testing sets
# grabs all the data up to the index from split index (first 75%)
data = data.iloc[:split_index]
data = data.dropna()
prices = data['close'].copy()
# for converting to numpy array
# prices = data['close'].astype(float).values
# print(prices)

# Convert prices to a Pandas Series
# prices_series = pd.Series(prices, index=data.index)
# print(prices_series)

# Create the dataset with windowing method
def create_dataset(prices, window_size):
    data = []
    for i in range(len(prices) - window_size):
        X = prices[i:i + window_size]
        y = prices[i + window_size]
        data.append(list(X) + [y])
    columns = [f't-{i}' for i in range(window_size, 0, -1)] + ['t']
    return pd.DataFrame(data, columns=columns)

window_size = 40
dataset = create_dataset(prices, window_size)
# print(dataset)
X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]
# print(X)
# print(y)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Normalize features and target using the training data
scaler = MinMaxScaler()
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

y_train = y_train.values.reshape(-1, 1)
y_test = y_test.values.reshape(-1, 1)
y_scaler = MinMaxScaler()
y_scaler.fit(y_train)
y_train_scaled = y_scaler.transform(y_train)
y_test_scaled = y_scaler.transform(y_test)

# sanity check
# print(window_size == X_train.shape[1])

# Define the model
model = Sequential()
model.add(Dense(10, input_dim=window_size, activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(1))

# Compile the model with a lower learning rate
model.compile(optimizer=SGD(learning_rate=0.001), loss='mean_squared_error', metrics=[tf.keras.metrics.MeanAbsolutePercentageError()])

# Train the model
history = model.fit(X_train_scaled, y_train_scaled, epochs=200, batch_size=32, validation_split=0.2, verbose=1)

# Evaluate the model
loss = model.evaluate(X_test_scaled, y_test_scaled, verbose=2)
predictions = model.predict(X_test_scaled)

print(predictions)
# # Inverse transform the predictions and actual values
# y_test_scaled_inv = y_scaler.inverse_transform(y_test_scaled)
# predictions_inv = scaler.inverse_transform(predictions)

# Inverse transform the predictions and actual values
y_test_scaled_inv = y_scaler.inverse_transform(y_test_scaled).flatten()  # Flatten to match shape
predictions_inv = y_scaler.inverse_transform(predictions).flatten()

# print(type(y_test_scaled_inv))
# print(type(predictions_inv))

# Convert numpy arrays to DataFrames
df_actual = pd.DataFrame({'Actual': y_test_scaled_inv})
df_predicted = pd.DataFrame({'Predicted': predictions_inv})

# Concatenate DataFrames
df_combined = pd.concat([df_actual, df_predicted], axis=1)

# Print or use df_combined as needed
print(df_combined)

# Print actual and predicted values for the first 10 samples
for i in range(10):
    print(f'Actual: {y_test_scaled_inv[i]}, Predicted: {predictions_inv[i]}')

# Get the current timestamp and format it
current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Save the model in .keras format
model.save(f'{current_timestamp}_stock_price_prediction_model.keras')
print("Model saved successfully.")
