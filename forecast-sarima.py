import pandas as pd
import numpy as np
from datetime import timedelta
from pmdarima import auto_arima
import matplotlib.pyplot as plt

def forecast_next_days(file_name="data/output-20000101-20241123.csv", days=10):
    """
    Forecasts the next 'days' temperatures based on the last available date in the dataset using SARIMA.
    :param file_name: Path to the CSV file containing the temperature data.
    :param days: Number of days to forecast.
    :return: DataFrame with forecasted temperatures for the next 'days'.
    """
    try:
        # Read the CSV file and skip unnecessary rows
        data = pd.read_csv(file_name, skiprows=8, skip_blank_lines=False)
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found!")
        return None

    # Extract the daily data table (first table)
    daily_data_end_idx = data[data.iloc[:, 0].str.startswith("# Avg Yearly temperature", na=False)].index[0]
    daily_data = data.iloc[:daily_data_end_idx, :4]
    daily_data.columns = ["Date", "T", "T_10_DAYS_AVG", "K_D_10_DAYS"]
    daily_data = daily_data.dropna(subset=["Date", "T"])  # Drop rows without a Date or Temperature

    # Convert 'T' column to numeric
    daily_data["T"] = pd.to_numeric(daily_data["T"], errors="coerce")
    daily_data = daily_data.dropna(subset=["T"])  # Remove rows where 'T' could not be converted

    # Parse 'Date' column
    daily_data['Date'] = pd.to_datetime(daily_data['Date'], format='%Y-%m-%d')
    daily_data.set_index('Date', inplace=True)

    # Resample data for monthly averages
    data_monthly = daily_data['T'].resample('M').mean()

    # Train SARIMA model
    try:
        model = auto_arima(
            data_monthly,
            seasonal=True,
            m=12,
            stepwise=True,
            trace=True,
            error_action='ignore',
            suppress_warnings=True
        )
    except Exception as e:
        print(f"Error fitting SARIMA model: {e}")
        return None

    # Forecast for the required number of days
    forecast_months = max(1, (days // 30) + 1)  # Convert days to months
    forecast = model.predict(n_periods=forecast_months)

    # Generate proper forecast dates
    last_date = data_monthly.index[-1]
    forecast_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=forecast_months, freq='M')

    # Interpolate daily forecasts if needed
    daily_forecast_dates = pd.date_range(last_date + timedelta(days=1), periods=days, freq='D')
    daily_forecast = pd.Series(
        np.interp(
            range(len(daily_forecast_dates)),
            np.linspace(0, len(daily_forecast_dates) - 1, len(forecast_dates)),
            forecast
        ),
        index=daily_forecast_dates
    )

    # Create DataFrame for forecasted values
    forecast_df = pd.DataFrame({
        'Date': daily_forecast.index.strftime('%Y-%m-%d'),
        'Predicted Temperature (°C)': daily_forecast.values
    })

    # Plot the historical data and the forecast
    plt.figure(figsize=(10, 6))
    plt.plot(data_monthly, label='Historical Data', color='blue')
    plt.plot(forecast_dates, forecast, label='SARIMA Monthly Forecast', color='orange')
    plt.plot(daily_forecast.index, daily_forecast.values, label='Interpolated Daily Forecast', color='green')
    plt.legend()
    plt.title('Temperature Forecast using SARIMA')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.show()

    return forecast_df

# Example usage:
forecast_df = forecast_next_days(days=30)
if forecast_df is not None:
    print(forecast_df)
