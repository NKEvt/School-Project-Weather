# Import required libraries
import requests
import csv
import datetime
import config  # Importing configurations for API URLs, keys, etc.

# Function to fetch historical weather data from VisualCrossing API
def fetch_visualcrossing_weather_data(location, start_date, end_date):
    try:
        # Get the API key from the config file
        api_key = config.VISUALCROSSING_API_KEY
        # Base URL for the VisualCrossing API from config file
        base_url = config.VISUALCROSSING_API_TMPL.format(zip=location, start_dt=start_date, end_dt=end_date, type="metric", API_key=api_key)
        
        # Make a GET request to the API
        response = requests.get(base_url)
        # Raise an error if the response indicates a failure
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        # Print error message if there was an issue with the request
        print(f"Error fetching data from VisualCrossing API: {e}")
        return None

# Function to write weather data to CSV file
def write_to_csv(file_name, data):
    try:
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Header row for the CSV file
            writer.writerow(["Date", "Temperature (C)", "Conditions"])
            # Iterate through the days in the response and write data to CSV
            for day in data['days']:
                writer.writerow([day['datetime'], day['temp'], day['conditions']])
    except Exception as e:
        # Print error message if there was an issue writing to the file
        print(f"Error writing data to CSV file: {e}")

# Function to test VisualCrossing API
def test_visualcrossing_api():
    location = "Newark,NJ"
    # Define the start and end dates for fetching historical data (last 10 days)
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=10)
    # Format dates as strings in the required format
    end_date_str = end_date.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")

    # Fetch data from VisualCrossing API
    data = fetch_visualcrossing_weather_data(location, start_date_str, end_date_str)
    if data:
        # Write data to CSV if fetch was successful
        write_to_csv("visualcrossing_weather.csv", data)
        print("VisualCrossing: Data successfully written to CSV.")
    else:
        print("VisualCrossing: Failed to fetch data.")

# Function to fetch historical weather data from Open-Meteo API
def fetch_openmeteo_weather_data(latitude, longitude, start_date, end_date):
    try:
        # Base URL for the Open-Meteo API from config file
        base_url = config.OPEN_METEO_API_TMPL.format(lat=latitude, long=longitude, start_dt=start_date, end_date=end_date)
        
        # Make a GET request to the API
        response = requests.get(base_url)
        # Raise an error if the response indicates a failure
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        # Print error message if there was an issue with the request
        print(f"Error fetching data from Open-Meteo API: {e}")
        return None


# Function to write weather data to CSV file
def write_to_csv(file_name, data):
    try:
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Header row for the CSV file
            writer.writerow(["Date", "Temperature (C)", "Conditions"])
            # Iterate through the days and write data
            for day in data['days']:
                writer.writerow([day['datetime'], day['temp'], day['conditions']])
    except Exception as e:
        print(f"Error writing data to CSV file: {e}")

# Function to test VisualCrossing API

def test_visualcrossing_api():
    location = "Newark,NJ"
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=10)
    end_date_str = end_date.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")

    data = fetch_visualcrossing_weather_data(location, start_date_str, end_date_str)
    if data:
        write_to_csv("visualcrossing_weather.csv", data)
        print("VisualCrossing: Data successfully written to CSV.")
    else:
        print("VisualCrossing: Failed to fetch data.")

# Function to fetch historical weather data from Open-Meteo API
def fetch_openmeteo_weather_data(latitude, longitude, start_date, end_date):
    try:
        base_url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "temperature_unit": "celsius",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "America/New_York"
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Open-Meteo API: {e}")
        return None

# Function to write Open-Meteo data to CSV
def write_openmeteo_to_csv(file_name, data):
    try:
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Header row for the CSV file
            writer.writerow(["Date", "Max Temperature (C)", "Min Temperature (C)", "Precipitation (mm)"])
            # Iterate through the days and write data
            for date, temp_max, temp_min, precipitation in zip(data['daily']['time'],
                                                               data['daily']['temperature_2m_max'],
                                                               data['daily']['temperature_2m_min'],
                                                               data['daily']['precipitation_sum']):
                writer.writerow([date, temp_max, temp_min, precipitation])
    except Exception as e:
        print(f"Error writing Open-Meteo data to CSV file: {e}")

# Function to test Open-Meteo API
def test_openmeteo_api():
    latitude = 40.7357  # Newark, NJ
    longitude = -74.1724
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y-%m-%d")

    data = fetch_openmeteo_weather_data(latitude, longitude, start_date, end_date)
    if data:
        write_openmeteo_to_csv("openmeteo_weather.csv", data)
        print("Open-Meteo: Data successfully written to CSV.")
    else:
        print("Open-Meteo: Failed to fetch data.")

# Main function to execute all tests
def main():
    # print("Testing VisualCrossing API...")
    # test_visualcrossing_api()
    print("\nTesting Open-Meteo API...")
    test_openmeteo_api()

if __name__ == "__main__":
    main()
