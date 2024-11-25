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
    Loads and parses the CSV file for temperature data.
    """
    try:
        data = pd.read_csv(file_name, skiprows=8, skip_blank_lines=False)
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found!")
        return None

    daily_data_end_idx = data[data.iloc[:, 0].str.startswith("# Avg Yearly temperature", na=False)].index[0]
    daily_data = data.iloc[:daily_data_end_idx, :4]
    daily_data.columns = ["Date", "T", "T_10_DAYS_AVG", "K_D_10_DAYS"]
    daily_data = daily_data.dropna(subset=["Date", "T"])
    daily_data["T"] = pd.to_numeric(daily_data["T"], errors="coerce")
    daily_data = daily_data.dropna(subset=["T"])
    daily_data['Date'] = pd.to_datetime(daily_data['Date'], format='%Y-%m-%d')
    daily_data.set_index('Date', inplace=True)

    return daily_data

def prepare_features(data_monthly):
    """
    Prepares features and targets for the Random Forest model.
    """
    df = data_monthly.reset_index()
    datetime_index = df['Date']  # Save the datetime index
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['Lag1'] = df['T'].shift(1)
    df['Lag2'] = df['T'].shift(2)
    df = df.dropna()  # Remove rows with NaN values (due to lagging)

    features = df[['Month', 'Year', 'Lag1', 'Lag2']]
    features.index = datetime_index[df.index]  # Reapply the datetime index
    target = df['T']
    return features, target


def train_model(features, target, model_file):
    """
    Trains a Random Forest model or loads an existing one if available.
    """
    # Check if the model already exists
    if os.path.exists(model_file):
        print(f"Loading pre-trained model from {model_file}...")
        return joblib.load(model_file)

    try:
        print("Training a new Random Forest model...")
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate the model
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Model trained with Mean Squared Error: {mse:.2f}")

        # Save the trained model
        joblib.dump(model, model_file)
        print(f"Model saved to {model_file}")
        return model
    except Exception as e:
        print(f"Error training Random Forest model: {e}")
        return None

def call_model(features, model, days, historical_data):
    """
    Forecasts temperatures using a trained Random Forest model.
    Adjusts predictions to match historical temperature ranges.
    """
    # Prepare forecast features
    last_row = features.iloc[-1].copy()  # Copy to avoid modifying original data
    forecast_features = []
    predictions = []

    for i in range(days):
        next_month = (last_row['Month'] + (i // 30)) % 12 or 12  # Cycle through months
        next_year = last_row['Year'] + ((last_row['Month'] + (i // 30)) // 12)
        
        # Create new feature row
        current_features = {
            'Month': next_month,
            'Year': next_year,
            'Lag1': last_row['Lag1'],
            'Lag2': last_row['Lag2']
        }
        
        # Predict temperature for the current day
        current_features_df = pd.DataFrame([current_features])  # Convert to DataFrame with feature names
        prediction = model.predict(current_features_df)[0]
        predictions.append(prediction)
        
        # Update lags for the next iteration
        last_row['Lag2'] = last_row['Lag1']
        last_row['Lag1'] = prediction

    # Generate forecast dates starting from the last date in historical data
    last_date = historical_data.index[-1]
    forecast_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=days)

    # Adjust predictions based on historical data for the same month
    for i, date in enumerate(forecast_dates):
        month = date.month
        historical_month_temps = historical_data[historical_data.index.month == month]['T']
        if not historical_month_temps.empty:
            # Constrain forecast within historical min and max for the same month
            predictions[i] = np.clip(predictions[i], historical_month_temps.min(), historical_month_temps.max())

    # Prepare DataFrame for forecast output
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Predicted Temperature (°C)': predictions
    })

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(historical_data.index, historical_data['T'], label='Historical Data', color='blue')
    plt.plot(forecast_dates, predictions, label='Random Forest Forecast', color='orange')
    plt.legend()
    plt.title('Temperature Forecast using Random Forest')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.show()

    return forecast_df


####################
# main
def main(file_name="data/output-20000101-20241123.csv", days=10):
    """
    Main function to load data, train model, and forecast temperatures.
    """
    # Load and parse historical data
    daily_data = load_and_parse_csv(file_name)
    if daily_data is None:
        return None

    data_monthly = daily_data['T'].resample('ME').mean()  # Update 'M' to 'ME' to fix the FutureWarning
    features, target = prepare_features(data_monthly)

    # Define model file name based on input file name
    model_file = file_name.rsplit('.', 1)[0] + '_rf.pkl'
    model = train_model(features, target, model_file)
    if model is None:
        return None

    # Call the model with historical data for adjustment
    forecast_df = call_model(features, model, days, historical_data=daily_data)
    print(forecast_df)
    return forecast_df


# Example usage
if __name__ == "__main__":
    forecast_df = main(days=30)

"""
This script is structured similarly to your SARIMA-based script, making it easy to use and adapt for Random Forest regression.

Key Features:

    Feature Engineering:
        Created lag features (Lag1, Lag2) to capture temporal dependencies.
        Added Month and Year as additional features for the model.

    Model Training:
        Used RandomForestRegressor from sklearn.ensemble with default parameters.
        Saved and loaded the trained model using joblib.

    Forecasting:
        Adjusted the Year feature in the forecast to simulate future predictions.
        Dropped unnecessary features like Lag2 to simplify future inputs.

    Error Metrics:
        Calculated and displayed the Mean Squared Error (MSE) for the trained model.

    Visualization:
        Plotted historical data alongside forecasted values.

** Error: ValueError: The feature names should match those that were passed during fit.
Feature names seen at fit time, yet now missing: - Lag2

Key Adjustments to fix error of the first version: Model trained with Mean Squared Error: 3.16

    Feature Consistency:
        The Lag2 column is now always included in forecast_features_df during prediction.
        Missing lags (e.g., for future predictions) are filled with 0 as a placeholder.

    Iterative Feature Update:
        Simulates rolling future predictions by updating lag values (Lag1, Lag2) based on previously predicted values.

    Graceful Handling of Missing Data:
        Placeholder values like 0 are used for missing lagged features to avoid crashing.

    Consistent Feature Names:
        Ensures the names and order of features match those during training.

        
** To resolve the two problems in the output:

    *** Start Date of Predictions:
        Ensure that the forecast starts from the day after the last date in the input dataset (2024-11-24 in this case), not from 2024-12-01.

    *** Unrealistic Forecasted Temperatures:
        Implement post-processing to align the predicted temperatures with the observed range of historical data for the same month.
        For example, constrain December temperatures to realistic historical ranges.

Key Adjustments:

    Forecast Start Date:
        The forecast_dates now start from the day after the last date in the historical data, using historical_data.index[-1] + pd.Timedelta(days=1).

    Historical Data Alignment:
        For each forecasted date, the month is extracted, and the historical temperature range (min and max) for that month is determined.
        The forecasted temperature is constrained within the historical range using np.clip.

    Realistic December Temperatures:
        If the historical data shows no temperatures above 13°C for December, the forecast for December will also adhere to this constraint.

** TypeError: call_model() missing 1 required positional argument: 'historical_data'
Explanation of the Fix:

    Pass historical_data:
        The daily_data DataFrame is now passed as historical_data to the call_model function.

    FutureWarning:
        The resampling frequency 'M' is updated to 'ME' to avoid the FutureWarning.

        
** The issue of identical predictions for all dates is likely due to how the Lag1 and Lag2 features are being updated during the forecast loop in the call_model function. Specifically, the Lag1 and Lag2 values are not dynamically updated based on predictions for previous days.
To fix this, we need to update the lag values (Lag1 and Lag2) in each iteration based on the predicted temperature for the previous day. This will ensure that the forecast evolves over time.

GPT

The issue of identical predictions for all dates is likely due to how the Lag1 and Lag2 features are being updated during the forecast loop in the call_model function. Specifically, the Lag1 and Lag2 values are not dynamically updated based on predictions for previous days.

To fix this, we need to update the lag values (Lag1 and Lag2) in each iteration based on the predicted temperature for the previous day. This will ensure that the forecast evolves over time.

Key Changes:

    Dynamic Lag Updates:
        The Lag1 and Lag2 features are updated iteratively. Lag1 is set to the current prediction, and Lag2 is set to the previous Lag1.

    Feature Updates for Each Iteration:
        A current_features dictionary is created for each day, ensuring the features are correctly updated based on the evolving predictions.

    Clipping Predictions:
        Predictions are constrained to the historical range for the same month to ensure they remain realistic.

    Avoiding Constant Values:
        By dynamically updating the lags, the model generates evolving predictions instead of constant values.

        
*** UserWarning: X does not have valid feature names, but RandomForestRegressor was fitted with feature names
To resolve this issue, ensure that the feature data passed to the model.predict method is always a Pandas DataFrame with the correct feature names.

"""