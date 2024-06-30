import datetime
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
from sklearn.preprocessing import RobustScaler


class StockPricePrediction:
    def __init__(self, data_path, window_size=40):
        self.data_path = data_path
        self.window_size = window_size
        self.model = None
        self.scaler = RobustScaler()
        self.y_scaler = RobustScaler()
    
    def load_and_preprocess_data(self):
        data = pd.read_csv(self.data_path, parse_dates=True, index_col='Date')
        data_create = data['Close'].copy()
        return data, data_create

    def create_dataset(self, prices):
        data = []
        for i in range(len(prices) - self.window_size):
            X = prices[i:i + self.window_size]
            y = prices.iloc[i + self.window_size]
            data.append(list(X) + [y])
        columns = [f't-{i}' for i in range(self.window_size, 0, -1)] + ['t']
        return pd.DataFrame(data, columns=columns)

    def normalize_data(self, X_train, y_train):
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        y_train = y_train.values.reshape(-1, 1)
        self.y_scaler.fit(y_train)
        y_train_scaled = self.y_scaler.transform(y_train)
        return X_train_scaled, y_train_scaled

    def inverse_transform(self, y_scaled, predictions_scaled):
        y_inv = self.y_scaler.inverse_transform(y_scaled).flatten()
        predictions_inv = self.y_scaler.inverse_transform(predictions_scaled).flatten()
        return y_inv, predictions_inv

    def build_model(self):
        model = Sequential()
        model.add(Dense(10, input_dim=self.window_size, activation='relu'))
        model.add(Dense(10, activation='relu'))
        model.add(Dense(10, activation='relu'))
        model.add(Dense(1))
        model.compile(optimizer=SGD(learning_rate=0.001), loss='mean_squared_error', metrics=[tf.keras.metrics.MeanAbsolutePercentageError()])
        self.model = model

    def train_model(self, X_train_scaled, y_train_scaled, epochs=50):
        self.model.fit(X_train_scaled, y_train_scaled, epochs=epochs, batch_size=32, validation_split=0.2, verbose=1)

    def evaluate_model(self, X_test_scaled, y_test_scaled):
        loss = self.model.evaluate(X_test_scaled, y_test_scaled, verbose=2)
        predictions = self.model.predict(X_test_scaled)
        return loss, predictions

    def save_model(self, epochs):
        current_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        model_path = f'models/{current_timestamp}_stock_price_prediction_model_epochs_{epochs}.keras'
        self.model.save(model_path)
        print("Model saved successfully.")
        return model_path