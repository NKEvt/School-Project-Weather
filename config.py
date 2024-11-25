import os
# Wheather APIs configuration
# API key must be kept in OS environment vars
################################
# WEATHER_CROSSING_API
# API sample call 01/01/2010 - 11/20/2024 : 
# https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/07302/2010-01-01/2024-11-20?unitGroup=us&include=hours%2Cdays&key=KEY&contentType=json
# https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/40.7282%2C-74.0776/2010-01-01/2024-11-20?unitGroup=metric&include=hours%2Cdays&key=H6UBQWH74ZE49PVNUE8KXXCPN&contentType=json
# API URL template
VISUALCROSSING_API_TMPL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{zip}/{start_dt}/{end_dt}?unitGroup={type}&include=hours,days&key={API_key}&contentType=json"
# Possible values:
# type : us, metric
# Store API keys (You can set these as environment variables as well)
VISUALCROSSING_API_KEY = os.getenv('VISUALCROSSING_API_KEY')

################################
# OPEN_METEO_API
# No API key required!
# Sample call  01/01/2010 - 11/20/2024 :
# https://archive-api.open-meteo.com/v1/era5?latitude=40.7282&longitude=-74.0776&start_date=2010-01-01&end_date=2024-11-22&hourly=temperature_2m

# API URL template
OPEN_METEO_API_TMPL = "https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={long}&start_date={start_dt}&end_date={end_dt}&hourly=temperature_2m"



# Set the default API you want to use (can be dynamically changed)
# Options: "OPEN_METEO_API" or "WEATHER_CROSSING_API"
DEFAULT_API = "OPEN_METEO_API"  


