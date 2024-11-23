import requests
import json
from config import OPENWEATHERMAP_API_KEY, WEATHER_CROSSING_API_KEY, OPENWEATHERMAP_API_URL, WEATHER_CROSSING_API_URL, DEFAULT_API

def get_weather_openweathermap(zip_code):
    url = f"{OPENWEATHERMAP_API_URL}?zip={zip_code}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data from OpenWeatherMap: {response.status_code}")
        return None

def get_weather_weather_crossing(zip_code):
    url = f"{WEATHER_CROSSING_API_URL}?zip={zip_code}&apikey={WEATHER_CROSSING_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data from WeatherCrossing: {response.status_code}")
        return None

def get_weather_data(zip_code):
    # Choose API based on the configuration (or environment variable)
    if DEFAULT_API == "openweathermap":
        return get_weather_openweathermap(zip_code)
    elif DEFAULT_API == "weather_crossing":
        return get_weather_weather_crossing(zip_code)
    else:
        print("Invalid API choice!")
        return None

zip_code='07302';
get_weather_data(zip_code);
