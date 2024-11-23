import os

# Store API URLs
OPENWEATHERMAP_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_CROSSING_API_URL = "https://weather-crossing-api.com/data"

# Store API keys (You can set these as environment variables as well)
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
WEATHER_CROSSING_API_KEY = os.getenv('WEATHER_CROSSING_API_KEY')

# Set the default API you want to use (can be dynamically changed)
DEFAULT_API = "weather_crossing"  # Options: "openweathermap" or "weather_crossing"

