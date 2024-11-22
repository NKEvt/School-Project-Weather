import requests
import csv
from datetime import datetime, timedelta
import os

# Function to collect historical weather data via API (Mode 1: Data Collection)
def collect_historical_weather_data(api_url, api_key, year, times_of_day):
    headers = {'Content-Type': 'application/json'}
    
    # Prepare the start and end dates for the year
    start_date = f'{year}-01-01'
    end_date = f'{year}-12-31'

    # Create a list to hold all the temperature data
    all_data = []

    # Loop over each day in the year and get hourly weather data
    for day_offset in range(365):  # Loop through days of the year (adjust if it's a leap year)
        # Calculate the date for the current day
        current_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        
        # Convert date to Unix timestamp for the API request
        timestamp = int(datetime.strptime(current_date, '%Y-%m-%d').timestamp())
        
        # Request hourly data from OpenWeatherMap
        params = {'lat': 40.730610, 'lon': -73.935242, 'dt': timestamp, 'appid': api_key, 'units': 'metric'}
        response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall/timemachine', params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check the hourly data for the required times
            for hourly_data in data['hourly']:
                # Extract the hour from the time
                hour = datetime.utcfromtimestamp(hourly_data['dt']).strftime('%H:%M')
                
                # If the hour matches one of the desired times, store the data
                if hour in times_of_day:
                    date_time = datetime.utcfromtimestamp(hourly_data['dt']).strftime('%Y-%m-%d %H:%M:%S')
                    temp_celsius = hourly_data['temp']
                    temp_fahrenheit = (temp_celsius * 9/5) + 32  # Convert Celsius to Fahrenheit
                    
                    all_data.append([current_date, date_time, temp_celsius, temp_fahrenheit])
        else:
            print(f"Error fetching data for {current_date}: {response.status_code}")
    
    # Write the collected data to a CSV file
    filename = f"{year}-temp.csv"
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Time', 'Temperature (°C)', 'Temperature (°F)'])
        for row in all_data:
            writer.writerow(row)
    
    print(f"Data for {year} collected and stored in {filename}")

# Example of running Mode 1: Collect historical data for 2021 with times 04:00, 10:00, 16:00, and 22:00
api_url = 'https://api.openweathermap.org/data/2.5/onecall/timemachine'
api_key = '4f70f224cd3a0d3c49caeb8f502637f8'  # Your OpenWeatherMap API key
year = 2021
times_of_day = ['04:00', '10:00', '16:00', '22:00']

collect_historical_weather_data(api_url, api_key, year, times_of_day)
