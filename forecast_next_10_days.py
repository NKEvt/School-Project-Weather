import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import argparse


def forecast_next_days(file_name="data/output-20000101-20241123.csv", days=10):
    """
    Forecasts the next 'days' temperatures based on the last available date in the dataset.
    :param file_name: Path to the CSV file containing the temperature data.
    :param days: Number of days to forecast.
    :return: DataFrame with forecasted temperatures for the next 'days'.
    """
    try:
        data = pd.read_csv(file_name, skiprows=8, skip_blank_lines=False)
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found!")
        return None

    # Extract the daily data table (first table)
    daily_data_end_idx = data[data.iloc[:, 0].str.startswith("# Avg Yearly temperature", na=False)].index[0]
    daily_data = data.iloc[:daily_data_end_idx, :4]
    daily_data.columns = ["Date", "T", "T_10_DAYS_AVG", "K_D_10_DAYS"]
    daily_data = daily_data.dropna(subset=["Date", "T"])  # Drop rows without a Date or Temperature

    # Convert 'T' column to numeric, coercing errors
    daily_data["T"] = pd.to_numeric(daily_data["T"], errors="coerce")
    daily_data = daily_data.dropna(subset=["T"])  # Remove rows where 'T' could not be converted

    # Parse 'Date' column in the daily data table
    try:
        daily_data['Date'] = pd.to_datetime(daily_data['Date'], format='%Y-%m-%d')
    except ValueError:
        print("Error: 'Date' column is not in 'YYYY-MM-DD' format and couldn't be parsed!")
        return None


    # Extract the yearly data table
    yearly_data_start_idx = daily_data_end_idx + 2
    yearly_data = data.iloc[yearly_data_start_idx:, :3]
    yearly_data.columns = ["Year", "T_Y_AVG", "K_Y_AVG"]
    yearly_data = yearly_data.dropna(subset=["Year", "T_Y_AVG"])
    yearly_data["Year"] = pd.to_numeric(yearly_data["Year"], errors="coerce")
    yearly_data["T_Y_AVG"] = pd.to_numeric(yearly_data["T_Y_AVG"], errors="coerce")
    yearly_data = yearly_data.dropna()

    # Prepare data for regression
    X = yearly_data["Year"].values.reshape(-1, 1)
    y = yearly_data["T_Y_AVG"].values
    model = LinearRegression()
    model.fit(X, y)

    # Model parameters
    slope = model.coef_[0]
    intercept = model.intercept_

    # Find the last available date
    last_date_dt = daily_data['Date'].max()

    # Historical daily variation by day of year
    daily_data["DayOfYear"] = daily_data["Date"].dt.dayofyear
    daily_variation = daily_data.groupby("DayOfYear")["T"].mean()

    # Forecast the next 'days' days
    forecast_dates = [(last_date_dt + timedelta(days=i)) for i in range(1, days + 1)]
    forecast_years = [date.year for date in forecast_dates]
    forecast_doy = [date.timetuple().tm_yday for date in forecast_dates]
    forecast_yearly_avg = [slope * year + intercept for year in forecast_years]

    # Incorporate daily variations
    forecast_temperatures = [
        forecast_yearly_avg[i] + daily_variation.get(doy, 0)
        for i, doy in enumerate(forecast_doy)
    ]

    # Create DataFrame for forecast
    forecast_df = pd.DataFrame({
        "Date": [date.strftime("%Y-%m-%d") for date in forecast_dates],
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
