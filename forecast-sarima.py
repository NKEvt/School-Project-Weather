import os
import joblib
import pandas as pd
from pmdarima import auto_arima
import logging

# Function to load and parse the CSV file
def load_and_parse_csv(file_name):
    """
    Loads, parses, and preprocesses the CSV file for temperature data.
    It handles two file formats: daily-avg.csv and openmeteo CSV.
    """
    try:
        # Load the data and inspect the columns
        data = pd.read_csv(file_name, skip_blank_lines=False)
        print(f"Loaded {file_name} with columns: {data.columns.tolist()}")
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found!")
        return None

    # Handle daily format
    if "daily" in file_name:
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

    # Drop rows with missing temperature values
    data = data.dropna(subset=["T"])

    # Set the Date column as index and enforce frequency
    data.set_index("Date", inplace=True)  # Ensure Date is set as index
    data = data.asfreq('D')  # Explicitly set daily frequency

    # Fill minor gaps with interpolation if necessary
    data['T'] = data['T'].interpolate(method='time')

    return data

# Function to train or load a SARIMA model
def train_model(data_daily, model_file):
    """
    Trains a SARIMA model or loads an existing one if available.
    """
    if os.path.exists(model_file):
        print(f"Loading pre-trained model from {model_file}...")
        return joblib.load(model_file)

    try:
        print("Training a new SARIMA model...")

        # enable logging
        logging.basicConfig(level=logging.DEBUG)

        # Use DayOfYear to reflect seasonality
        model = auto_arima(
            data_daily,
            seasonal=True,
            m=365,  # Yearly seasonality
            stepwise=True,
            suppress_warnings=True,
            max_order=5,
            d=1,  # Difference order
            D=1,  # Seasonal difference order
            maxiter=50,  # Limit iterations
            error_action='ignore',
            trace=True
        )
        # Save the trained model
        joblib.dump(model, model_file)
        print(f"Model saved to {model_file}")
        return model
    except Exception as e:
        print(f"Error fitting SARIMA model: {e}")
        return None

# Function to forecast using the SARIMA model
def sarima_forecast(model, start_date, days):
    """
    Uses the SARIMA model to forecast temperature for the specified days.
    """
    # Forecast for the specified number of days
    forecast = model.predict(n_periods=days, return_conf_int=True)
    forecast_df = pd.DataFrame({
        'Date': pd.date_range(start=start_date, periods=days),
        'Mean': forecast[0].round(2),  # Round mean temperature to 2 decimal places
        'Lower_CI': forecast[1][:, 0].round(2),  # Round lower confidence interval to 2 decimal places
        'Upper_CI': forecast[1][:, 1].round(2)   # Round upper confidence interval to 2 decimal places
    })
    return forecast_df

# Main function to tie it all together
def main(file_name, model_file, days=5):
    """
    Main function to load data, train/load the model, and run forecasting.
    """
    # Load and parse the data
    daily_data = load_and_parse_csv(file_name)
    if daily_data is None:
        return  # Exit if loading failed
    
    # Train or load the SARIMA model
    model = train_model(daily_data['T'], model_file)
    if model is None:
        print("Model training/loading failed. Exiting.")
        return
    
    # Get the last date in the dataset
    max_date = daily_data.index.max()
    start_date = max_date + pd.Timedelta(days=1)  # Start prediction from the next day
    
    # Perform SARIMA forecasting
    forecast_df = sarima_forecast(model, start_date, days)
    
    print(forecast_df)
    return forecast_df

# Run the main function
if __name__ == "__main__":
    input_file = "data/20100101-20241204/daily-max.csv"
    model_file = input_file.rsplit('.', 1)[0] + '_sarima.pkl'  # Path to cache the trained model
    forecast_df = main(input_file, model_file, days=5)
