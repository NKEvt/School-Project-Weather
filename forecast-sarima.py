import pandas as pd
import numpy as np
from datetime import timedelta
from pmdarima import auto_arima
import matplotlib.pyplot as plt

def load_and_parse_csv(file_name):
    """
    Loads and parses the CSV file for temperature data.
    :param file_name: Path to the CSV file.
    :return: Parsed DataFrame with temperature data.
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

def train_model(data_monthly):
    """
    Trains a SARIMA model on the provided monthly data.
    :param data_monthly: Monthly average temperature data.
    :return: Trained SARIMA model.
    """
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
        return model
    except Exception as e:
        print(f"Error fitting SARIMA model: {e}")
        return None

def forecast_temperature(file_name="data/output-20000101-20241123.csv", days=10):
    """
    Forecasts temperatures using a SARIMA model.
    :param file_name: Path to the CSV file containing temperature data.
    :param days: Number of days to forecast.
    :return: DataFrame with forecasted temperatures.
    """
    daily_data = load_and_parse_csv(file_name)
    if daily_data is None:
        return None

    data_monthly = daily_data['T'].resample('M').mean()
    model = train_model(data_monthly)
    if model is None:
        return None

    forecast_months = max(1, (days // 30) + 1)
    forecast = model.predict(n_periods=forecast_months)

    last_date = data_monthly.index[-1]
    forecast_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=forecast_months, freq='M')

    daily_forecast_dates = pd.date_range(last_date + timedelta(days=1), periods=days, freq='D')
    daily_forecast = pd.Series(
        np.interp(
            range(len(daily_forecast_dates)),
            np.linspace(0, len(daily_forecast_dates) - 1, len(forecast_dates)),
            forecast
        ),
        index=daily_forecast_dates
    )

    forecast_df = pd.DataFrame({
        'Date': daily_forecast.index.strftime('%Y-%m-%d'),
        'Predicted Temperature (°C)': daily_forecast.values
    })

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
forecast_df = forecast_temperature(days=30)
if forecast_df is not None:
    print(forecast_df)
