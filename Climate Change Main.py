import requests
import csv
from datetime import datetime, timedelta
import config


def fetch_openmeteo_weather_data(latitude, longitude, start_date, end_date):
    """Fetch weather data from Open-Meteo API."""
    try:
        base_url = config.OPEN_METEO_API_TMPL.format(
            lat=latitude, long=longitude, start_dt=start_date, end_dt=end_date
        )
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Open-Meteo API: {e}")
        return None


def calculate_moving_average(temperatures, window_size):
    """Calculate moving averages with a given window size."""
    moving_averages = []
    for i in range(len(temperatures)):
        if i < window_size - 1:
            moving_averages.append(None)
        else:
            window = temperatures[i - window_size + 1:i + 1]
            moving_averages.append(sum(window) / window_size)
    return moving_averages


def calculate_coefficients(daily_temps, moving_averages):
    """Calculate daily temperature coefficients."""
    coefficients = []
    for i in range(len(daily_temps)):
        if i == 0 or moving_averages[i] is None:
            coefficients.append(None)
        else:
            coefficients.append(daily_temps[i - 1] / moving_averages[i])
    return coefficients


def calculate_yearly_averages(daily_data):
    """Calculate average temperature for each year."""
    yearly_data = {}
    for date_str, temp in daily_data.items():
        year = date_str[:4]
        if year not in yearly_data:
            yearly_data[year] = []
        yearly_data[year].append(temp)
    yearly_averages = {}
    for year, temps in yearly_data.items():
        yearly_averages[year] = sum(temps) / len(temps)
    return yearly_averages


def calculate_yearly_coefficients(yearly_averages):
    """Calculate yearly temperature coefficients."""
    years = sorted(yearly_averages.keys())
    yearly_coefficients = {}
    for i in range(1, len(years)):
        current_year = years[i]
        previous_year = years[i - 1]
        if yearly_averages[previous_year] != 0:
            yearly_coefficients[current_year] = (
                yearly_averages[current_year] / yearly_averages[previous_year]
            )
        else:
            yearly_coefficients[current_year] = None
    return yearly_coefficients


def write_to_csv(daily_data, yearly_averages, yearly_coefficients, output_file):
    """Write processed data to CSV."""
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["# Daily temperature and moving averages"])
        writer.writerow(["Date (YYYYMMDD)", "T (°C)", "T_10_DAYS_AVG (°C)", "K_D_10_DAYS"])
        for date_str, data in daily_data.items():
            t_10_days_avg = data['T_10_DAYS_AVG']
            k_d_10_days = data['K_D_10_DAYS']
            writer.writerow([date_str, data['T'], t_10_days_avg, k_d_10_days])
        writer.writerow([])
        writer.writerow(["# Avg Yearly temperature"])
        writer.writerow(["Year", "T_Y_AVG (°C)", "K_Y_AVG"])
        for year, t_y_avg in yearly_averages.items():
            k_y_avg = yearly_coefficients.get(year, "")
            writer.writerow([year, t_y_avg, k_y_avg])


def main():
    # Define constants
    latitude = 40.7282
    longitude = -74.0776
    start_date = "2000-01-01"
    end_date = "2024-11-23"
    output_file = f"data/output-{start_date.replace('-', '')}-{end_date.replace('-', '')}.csv"


    # Step 1: Fetch data
    print("Fetching weather data...")
    data = fetch_openmeteo_weather_data(latitude, longitude, start_date, end_date)
    if not data or 'hourly' not in data or 'temperature_2m' not in data['hourly']:
        print("Error: No valid temperature data found!")
        return

    # Step 2: Process daily temperature data
    hourly_temps = data['hourly']['temperature_2m']
    times = data['hourly']['time']
    daily_data = {}
    for time, temp in zip(times, hourly_temps):
        date_str = time.split("T")[0]
        if date_str not in daily_data:
            daily_data[date_str] = []
        daily_data[date_str].append(temp)

    # Calculate daily averages
    daily_avg_temps = {
        date: sum(temps) / len(temps) for date, temps in daily_data.items()
    }

    # Sort dates for consistent processing
    sorted_dates = sorted(daily_avg_temps.keys())
    daily_temps_list = [daily_avg_temps[date] for date in sorted_dates]

    # Step 3: Compute moving averages and coefficients
    print("Calculating daily moving averages and coefficients...")
    t_10_days_avg_list = calculate_moving_average(daily_temps_list, 10)
    k_d_10_days_list = calculate_coefficients(daily_temps_list, t_10_days_avg_list)

    # Update daily_avg_temps with calculated values
    for i, date in enumerate(sorted_dates):
        daily_avg_temps[date] = {
            'T': daily_temps_list[i],
            'T_10_DAYS_AVG': t_10_days_avg_list[i],
            'K_D_10_DAYS': k_d_10_days_list[i],
        }

    # Step 4: Calculate yearly averages and coefficients
    print("Calculating yearly averages and coefficients...")
    yearly_averages = calculate_yearly_averages({
        date: temp['T'] for date, temp in daily_avg_temps.items()
    })
    yearly_coefficients = calculate_yearly_coefficients(yearly_averages)

    # Step 5: Write results to CSV
    print(f"Writing results to {output_file}...")
    write_to_csv(daily_avg_temps, yearly_averages, yearly_coefficients, output_file)

    print("Processing complete! Results saved to CSV.")


if __name__ == "__main__":
    main()
