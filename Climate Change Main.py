import requests
import csv
from datetime import datetime, timedelta
import os


# Function to collect weather data via API (Mode 1: Data Collection)
def collect_weather_data(api_url, api_key, start_date, end_date):
    headers = {'Content-Type': 'application/json'}
    params = {'key': api_key, 'start': start_date, 'end': end_date}
    
    # Make request to the API
    response = requests.get(api_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        # Extract the year from the start_date to create a file name
        year = start_date.split('-')[0]
        
        # Store data in a CSV file for the specified year
        filename = f"{year}-temp.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date', 'Time', 'Temperature (F)'])
            for entry in data['data']:
                date_time = entry['datetime']
                temp = (entry['temp'] * 9/5) + 32  # Convert from °C to °F
                writer.writerow([date_time.split('T')[0], date_time.split('T')[1], temp])
        print(f"Data collected and stored in {filename}")
    else:
        print("Error in API request:", response.status_code)

# Function to calculate K for each year and month (Mode 2: Calculate K)
def calculate_K(file_list):
    year_data = {}
    
    for file in file_list:
        year = file.split('-')[0]
        year_data[year] = []
        
        # Read the temperature data from the CSV file
        with open(file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                date = row[0]
                time = row[1]
                temp = float(row[2])
                year_data[year].append((date, time, temp))
    
    # Calculate K for each year (T(y) - T(y-1))
    K_results = {}
    for i in range(1, len(file_list)):
        curr_year = file_list[i].split('-')[0]
        prev_year = file_list[i-1].split('-')[0]
        K_results[curr_year] = {}
        
        for curr_entry, prev_entry in zip(year_data[curr_year], year_data[prev_year]):
            curr_date, curr_time, curr_temp = curr_entry
            prev_date, prev_time, prev_temp = prev_entry
            
            # Ensure matching dates and times
            if curr_date == prev_date and curr_time == prev_time:
                K = curr_temp - prev_temp  # Coefficient of warming (Fahrenheit)
                month = datetime.strptime(curr_date, '%Y-%m-%d').strftime('%B')
                if month not in K_results[curr_year]:
                    K_results[curr_year][month] = []
                K_results[curr_year][month].append(K)
    
    # Calculate average K per month and save to file
    output_filename = "year-coeff.csv"
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Year', 'Month', 'K (Fahrenheit)'])
        for year, months in K_results.items():
            for month, K_values in months.items():
                avg_K = sum(K_values) / len(K_values)
                writer.writerow([year, month, avg_K])
    
    print(f"K values calculated and stored in {output_filename}")

# Example of running Mode 1: Collect data from Jan 1st 2010 till Sep 6th 2024
api_url = 'https://api.weatherbit.io/v2.0/history/daily'
api_key = 'your_api_key'
start_date = '2010-01-01'
end_date = '2024-09-06'

collect_weather_data(api_url, api_key, start_date, end_date)

# Example of running Mode 2: Calculate K
file_list = ['2019-temp.csv', '2020-temp.csv', '2021-temp.csv', '2022-temp.csv']
calculate_K(file_list)

# Function to predict temperature based on K values
def predict_temperature(date, real_temp, year, K_file):
    month = datetime.strptime(date, '%Y-%m-%d').strftime('%B')
    
    # Load K values from file
    K_values = {}
    with open(K_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            yr, mnth, K = row
            if yr == str(year):
                K_values[mnth] = float(K)
    
    # If K for this year is not available, use previous year’s K
    if month not in K_values:
        print(f"K for {month} {year} is not available, using previous year")
        previous_year = year - 1
        with open(K_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                yr, mnth, K = row
                if yr == str(previous_year) and mnth == month:
                    K_values[month] = float(K)
                    break
    
    # Predict temperature
    if month in K_values:
        predicted_temp = real_temp + K_values[month]
        return predicted_temp
    else:
        print(f"No K value available for {month}")
        return None

# Mode 1: Interactive Mode
def interactive_mode():
    date = input("Enter date (YYYY-MM-DD): ")
    time = input("Enter time (HH:MM): ")
    real_temp = float(input("Enter real temperature in Fahrenheit: "))
    year = int(date.split('-')[0])
    
    predicted_temp = predict_temperature(date, real_temp, year, 'year-coeff.csv')
    if predicted_temp:
        print(f"Predicted temperature: {predicted_temp:.2f} °F")
        print(f"Deviation: {real_temp - predicted_temp:.2f} °F")

# Mode 2: Predict Mode (using K for 2024)
def predict_mode():
    date = input("Enter date (YYYY-MM-DD): ")
    time = input("Enter time (HH:MM): ")
    real_temp = float(input("Enter real temperature in Fahrenheit: "))
    
    predicted_temp = predict_temperature(date, real_temp, 2024, 'year-coeff.csv')
    
    if predicted_temp:
        print(f"Predicted temperature for {date}: {predicted_temp:.2f} °F")
        print(f"Real temperature: {real_temp:.2f} °F")
        print(f"Deviation: {real_temp - predicted_temp:.2f} °F")

# Run the interactive mode
interactive_mode()

# Run the predict mode for 2024
predict_mode()

