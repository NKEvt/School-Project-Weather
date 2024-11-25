import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import argparse
# python forecast_next_10_days.py --file data/output-20000101-20241123.csv --days 10


def forecast_next_days(file_name="data/output-20000101-20241123.csv", days=10):
    """
    Forecasts the next 'days' temperatures based on the last available date in the dataset.
    :param file_name: Path to the CSV file containing the temperature data.
    :param days: Number of days to forecast.
    :return: DataFrame with forecasted temperatures for the next 'days'.
    """
    # Load the historical temperature data
    try:
        data = pd.read_csv(file_name, skiprows=8)  # Skip comment lines
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found!")
        return None

    data.columns = data.columns.str.strip()

    # Extract Yearly Average Temperatures
    yearly_data = data.iloc[:, 1:]  # Focus on the yearly data table
    yearly_data.columns = ["Year", "T_Y_AVG", "K_Y_AVG"]
    yearly_data = yearly_data.dropna(subset=["Year", "T_Y_AVG"])  # Remove invalid rows
    yearly_data["Year"] = pd.to_numeric(yearly_data["Year"], errors="coerce")
    yearly_data["T_Y_AVG"] = pd.to_numeric(yearly_data["T_Y_AVG"], errors="coerce")
    yearly_data = yearly_data.dropna()  # Drop rows with parsing issues

    # Prepare data for regression
    X = yearly_data["Year"].values.reshape(-1, 1)  # Features (Years)
    y = yearly_data["T_Y_AVG"].values  # Target (Average Temperatures)

    # Train a linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Model parameters
    slope = model.coef_[0]
    intercept = model.intercept_

    # Find the last available date in the dataset
    daily_data = data.iloc[:, :4]  # Focus on the daily data table
    daily_data.columns = ["Date", "T", "T_10_DAYS_AVG", "K_D_10_DAYS"]
    daily_data = daily_data.dropna(subset=["Date"])  # Ensure 'Date' column has valid data
    last_date = daily_data["Date"].iloc[-1]
    last_date_dt = datetime.strptime(str(int(last_date)), "%Y%m%d")

    # Forecast the next 'days' days
    forecast_dates = [(last_date_dt + timedelta(days=i)).strftime("%Y%m%d") for i in range(1, days + 1)]
    forecast_years = [datetime.strptime(date, "%Y%m%d").year for date in forecast_dates]
    forecast_temperatures = [slope * year + intercept for year in forecast_years]

    # Create DataFrame for forecast
    forecast_df = pd.DataFrame({
        "Date": forecast_dates,
        "Predicted Temperature (°C)": forecast_temperatures
    })

    return forecast_df


if __name__ == "__main__":
    # Parse script arguments
    parser = argparse.ArgumentParser(description="Forecast temperatures for the next N days.")
    parser.add_argument("--file", type=str, default="data/output-20000101-20241123.csv",
                        help="Path to the CSV file containing temperature data.")
    parser.add_argument("--days", type=int, default=10,
                        help="Number of days to forecast. Default is 10.")
    args = parser.parse_args()

    # Generate forecast
    forecast = forecast_next_days(file_name=args.file, days=args.days)

    if forecast is not None:
        print("\nForecast for the next days:")
        print(forecast)
        forecast.to_csv("forecast_output.csv", index=False)
        print("\nForecast saved to 'forecast_output.csv'.")
