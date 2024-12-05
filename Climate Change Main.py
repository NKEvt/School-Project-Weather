import os
import csv
from datetime import datetime
from collections import defaultdict
import requests
import config


def fetch_openmeteo_weather_data(latitude, longitude, start_date, end_date, calc_logic='max', enforce_api_call=False):
    """
    Fetch weather data from Open-Meteo API, caching the results in a file in the `data` folder.
    The cached file contains `time` and `temperature`. Depending on `calc_logic`, return daily max, min, or avg temperature.
    """
    # Ensure the `data` directory exists


    # Define the cache file path
    cache_file = f"{data_dir}/openmeteo-{start_date.replace('-', '')}-{end_date.replace('-', '')}.csv"

    # Fetch fresh data from API if enforce_api_call is True or cache doesn't exist
    if enforce_api_call or not os.path.exists(cache_file) or os.path.getsize(cache_file) == 0:
        print("Fetching fresh data from API...")
        try:
            base_url = config.OPEN_METEO_API_TMPL.format(
                lat=latitude, long=longitude, start_dt=start_date, end_dt=end_date
            )
            response = requests.get(base_url)
            response.raise_for_status()
            json_data = response.json()

            # Validate response data
            if "hourly" not in json_data or "temperature_2m" not in json_data["hourly"]:
                print("Error: API response does not contain valid temperature data.")
                return None

            # Extract hourly data
            hourly_data = json_data["hourly"]
            hourly_records = [
                {"time": time, "temperature": temp}
                for time, temp in zip(hourly_data["time"], hourly_data["temperature_2m"])
                if temp is not None  # Exclude rows without temperature
            ]

            # Save data to cache file
            with open(cache_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["time", "temperature"])
                writer.writeheader()
                writer.writerows(hourly_records)
            print(f"Data cached to file: {cache_file}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Open-Meteo API: {e}")
            return None

    # Read data from cache file
    print(f"Reading data from cache: {cache_file}")
    daily_data = defaultdict(list)
    with open(cache_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            time = row["time"]
            temp_str = row["temperature"]
            # Validate temperature value
            if temp_str.strip():  # Skip empty or whitespace-only strings
                try:
                    temperature = float(temp_str)
                    date = time.split("T")[0]  # Extract the date part
                    daily_data[date].append(temperature)
                except ValueError:
                    print(f"Skipping invalid temperature value: {temp_str} at time {time}")

    # Calculate daily temperature based on calc_logic
    formatted_data = []
    for date, temperatures in daily_data.items():
        if temperatures:  # Ensure there's at least one valid temperature
            if calc_logic == 'avg':
                result_temp = round(sum(temperatures) / len(temperatures),2)
                
            elif calc_logic == 'min':
                result_temp = min(temperatures)
            else:  # Default to 'max'
                result_temp = max(temperatures)

            formatted_data.append({"date": date, "temperature": result_temp})

    return formatted_data

def calculate_daily_averages(data):
    """
    Calculate the daily averages from the weather data.
    This assumes 'data' is a list of dictionaries with 'date' and 'temperature'.
    """
    daily_averages_ret = {}
    for entry in data:
        date = entry['date']
        temperature = entry['temperature']

        if date not in daily_averages_ret:
            daily_averages_ret[date] = []
        daily_averages_ret[date].append(temperature)

    # Now calculate the average temperature for each day
    for date, temps in daily_averages_ret.items():
        daily_averages_ret[date] = round(sum(temps) / len(temps), 2)

    return daily_averages_ret

def calculate_yearly_averages(daily_data):
    """
    Calculate average temperature for each year and yearly temperature coefficients (change from the previous year).
    """
    yearly_data = {}
    
    # Step 1: Aggregate temperature data for each year
    for date_str, temp in daily_data.items():
        year = date_str[:4]
        
        # Ensure temp is a number (float or int)
        try:
            temp = float(temp)  # Convert temp to float if it's not already
        except (ValueError, TypeError):
            print(f"Warning: Skipping invalid temperature data for {date_str}: {temp}")
            continue  # Skip invalid data

        if year not in yearly_data:
            yearly_data[year] = []
        yearly_data[year].append(temp)

    # Step 2: Calculate yearly averages
    yearly_averages = {}
    for year, temps in yearly_data.items():
        if temps:  # Ensure that there are temperatures to calculate
            yearly_averages[year] = {
                'TEMPERATURE': round(sum(temps) / len(temps),2),  # Calculate average temperature for the year
                'CHANGE': 1  # Placeholder for temperature change (to be calculated next)
            }
        else:
            print(f"Warning: No valid data for year {year}")
            yearly_averages[year] = {
                'TEMPERATURE': None,
                'CHANGE': None
            }

    # Step 3: Calculate yearly temperature coefficients (change from previous year)
    for year in sorted(yearly_averages.keys())[1:]:  # Start from the second year
        prev_year = str(int(year) - 1)
        if prev_year in yearly_averages and yearly_averages[prev_year]['TEMPERATURE'] is not None:
            prev_temp = yearly_averages[prev_year]['TEMPERATURE']
            current_temp = yearly_averages[year]['TEMPERATURE']
            if prev_temp != 0:  # Avoid division by zero
                change = round(current_temp / prev_temp,2)
            else:
                change = 1
            yearly_averages[year]['CHANGE'] = change

    return yearly_averages

def write_daily_data_to_csv(daily_data):
    """
    Write daily data to CSV.
    """
    output_file = f"{data_dir}/daily-{calc_logic}.csv"
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "TEMPERATURE"])
        
        # Write each date's average temperature
        for date_str, temperature in daily_data.items():
            writer.writerow([date_str, temperature])

    print(f"Daily data saved to {output_file}")


def write_yearly_averages_to_csv(yearly_averages):
    """
    Write yearly averages data to CSV.
    """
    output_file = f"{data_dir}/yearly-{calc_logic}.csv"

    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Year", "TEMPERATURE", "CHANGE"])
        
        # Write each year's data (TEMPERATURE and CHANGE)
        for year, data in yearly_averages.items():
            writer.writerow([year, data['TEMPERATURE'], data['CHANGE']])
    
    print(f"Yearly averages saved to {output_file}")


def main():
    # Define constants
    latitude = 40.7282 # latitude of Jersey City 
    longitude = -74.0776 # longitude of Jersey City 
    global data_dir, calc_logic

    # calc_logic, start_date, end_date = "avg", "1994-01-01", "2023-12-31"
    # calc_logic, start_date, end_date = "avg", "2021-01-01", "2023-12-31"
    # calc_logic, start_date, end_date = "avg", "1984-01-01", "2023-12-31"
    
    # calc_logic, start_date, end_date = "max", "1984-01-01", "2023-12-31"
    # calc_logic, start_date, end_date = "avg", "1984-01-01", "2023-12-31"
    # calc_logic, start_date, end_date = "max", "1964-01-01", "2023-12-31"
    # calc_logic, start_date, end_date = "avg", "1964-01-01", "2023-12-31"
    # calc_logic, start_date, end_date = "min", "1964-01-01", "2023-12-31"
    calc_logic, start_date, end_date = "avg", "2023-01-01", "2024-12-04"
    
    data_dir=f"data/{start_date.replace('-', '')}-{end_date.replace('-', '')}"
    # Ensure the `data` directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Step 1: Fetch data
    print("Fetching weather data...")
    data = fetch_openmeteo_weather_data( latitude, longitude, start_date, end_date, calc_logic )
    if not data or not isinstance(data, list) or len(data) == 0:
        print("Error: No valid temperature data found!")
        return

    # Step 2: Process daily temperature data
    print("Calculating daily averages ...")
    daily_avg  = calculate_daily_averages(data)

    # Step 3: Calculate yearly averages and coefficients
    print("Calculating yearly averages and coefficients...")
    yearly_averages  = calculate_yearly_averages(daily_avg)


    # Step 4: Write results to CSV
    print("Saving data into CSV...")
    write_daily_data_to_csv(daily_avg)
    write_yearly_averages_to_csv(yearly_averages)

    print("Processing complete! Results saved to CSV.")

if __name__ == "__main__":
    main()
