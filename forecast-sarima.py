import pandas as pd
import numpy as np
from pmdarima import auto_arima
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Load data
data = pd.read_csv('data/output-20000101-20241123.csv')
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Ensure data is in monthly average format for SARIMA
data_monthly = data.resample('M').mean()

# Train SARIMA model
sarima_model = auto_arima(
    data_monthly['Temperature (C)'], 
    seasonal=True, 
    m=12,  # Monthly seasonality
    stepwise=True, 
    suppress_warnings=True
)

# Forecasting future temperatures
n_periods = 12  # Forecast 12 months ahead
sarima_forecast = sarima_model.predict(n_periods=n_periods)

# Plot SARIMA results
future_dates = pd.date_range(data_monthly.index[-1], periods=n_periods + 1, freq='M')[1:]
plt.figure(figsize=(10, 6))
plt.plot(data_monthly, label='Historical Data')
plt.plot(future_dates, sarima_forecast, label='SARIMA Forecast', color='orange')
plt.legend()
plt.title('Temperature Forecast using SARIMA')
plt.show()
