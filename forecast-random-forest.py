
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import joblib  # For saving and loading models

def load_and_parse_csv(file_name):
    """
    Loads and parses the CSV file for temperature data based on the format.
    It handles two file formats: daily-avg.csv and openmeteo CSV.
    """
    try:
        # Load the data and inspect the columns
        data = pd.read_csv(file_name, skip_blank_lines=False)
        print(f"Loaded {file_name} with columns: {data.columns.tolist()}")
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found!")
        return None

    # Handle daily-avg.csv format
    if "daily-avg.csv" in file_name:
        data.columns = data.columns.str.strip().str.lower()
        data["Date"] = pd.to_datetime(data["date"])
        data = data.rename(columns={"temperature": "T"})
        data["DayOfYear"] = data["Date"].dt.dayofyear
        data = data[["Date", "T", "DayOfYear"]]

    # Handle openmeteo CSV format
    elif "openmeteo" in file_name:
        data.columns = data.columns.str.strip().str.lower()
        data["Date"] = pd.to_datetime(data["time"].str[:10])  # Extract date part
        data["T"] = data["temperature"]
        data["DayOfYear"] = data["Date"].dt.dayofyear
        data = data[["Date", "T", "DayOfYear"]]

    else:
        raise ValueError(f"Unknown file format for '{file_name}'.")

    data = data.dropna(subset=["T"])  # Drop rows with missing temperature values
    return data

def prepare_features(data):
    """
    Prepare features for predicting the next 10 days of temperature.
    Includes lags, moving averages, and seasonal indicators.
    """
    # Add lag features for the last 10 days
    for lag in range(1, 11):
        data[f'T_Lag_{lag}'] = data['T'].shift(lag)

    # Add moving averages
    data['T_MA_3'] = data['T'].rolling(window=3).mean()
    data['T_MA_5'] = data['T'].rolling(window=5).mean()
    data['T_MA_10'] = data['T'].rolling(window=10).mean()

    # Add seasonal features
    data['DayOfYear'] = data['Date'].dt.dayofyear

    # Drop rows with NaN values (due to shifting and rolling)
    data = data.dropna()

    # Create feature set (X) and target (y)
    X = data.drop(columns=['Date', 'T'])
    y = data['T']

    return data, X, y


def train_model(X, y):
    """
    Train the Random Forest model using the provided features (X) and target (y).
    """
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def evaluate_model(model, X, y):
    """
    Evaluate the model performance using mean squared error.
    """
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    return mse

def plot_predictions(data, model):
    """
    Plot the actual vs predicted temperature values.
    """
    X, y = prepare_features(data)
    y_pred = model.predict(X)
    
    # Filter 'Date' to match the rows used in `y`
    filtered_dates = data.loc[X.index, 'Date']
    
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_dates, y, label='Actual Temperature', color='blue')
    plt.plot(filtered_dates, y_pred, label='Predicted Temperature', color='red', linestyle='dashed')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.title('Actual vs Predicted Temperatures')
    plt.legend()
    plt.show()

def main():
    # Load data from CSV files
    # file_names = [ "data/20230101-20241204/daily-avg.csv", "data/20230101-20241204/openmeteo-20230101-20241204.csv" ]
    file_names = [ "data/20230101-20241204/openmeteo-20230101-20241204.csv" ]
    
    # Load and combine data
    data_frames = [load_and_parse_csv(file) for file in file_names]
    combined_data = pd.concat(data_frames, ignore_index=True)
    
    # Prepare features and target for training
    combined_data, X, y = prepare_features(combined_data)
    
    # Train the Random Forest model
    model = train_model(X, y)
    
    # Evaluate the model
    mse = evaluate_model(model, X, y)
    print(f"Model Mean Squared Error: {mse}")
    
    # Predict the next 10 days
    print("Preparing next 10 days of predictions...")
    
    # Extract the last 10 rows of the dataset
    recent_data = combined_data.iloc[-10:].copy()
    X_recent = recent_data.drop(columns=['Date', 'T'])
    predictions = model.predict(X_recent)
    
    # Calculate the next 10 dates
    last_date = combined_data['Date'].max()
    next_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 11)]
    
    # Print predictions with dates
    print("Next 10 Days Predictions:")
    for date, prediction in zip(next_dates, predictions):
        print(f"{date.strftime('%Y-%m-%d')}: {prediction:.2f}°C")

if __name__ == "__main__":
    main()
