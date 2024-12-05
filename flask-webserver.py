import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_from_directory

# Initialize Flask app
app = Flask(__name__)

# Create 'static' directory if not exists
if not os.path.exists('static'):
    os.makedirs('static')

def generate_plot():
    # URL of the CSV file
    url = 'https://raw.githubusercontent.com/NKEvt/School-Project-Weather/refs/heads/development/data/19640101-20231231/yearly-max.csv'

    # Download CSV from the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching CSV: {response.status_code}")
        return None  # Return None if the download fails
    
    with open("yearly-max.csv", "wb") as file:
        file.write(response.content)

    # Load the data into pandas DataFrame
    try:
        data = pd.read_csv("yearly-max.csv")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None  # Return None if there's an error loading the CSV

    # Extract the start and end years dynamically from the data
    start_year = data['Year'].min()
    end_year = data['Year'].max()

    # Print start and end years for debugging
    print(f"Start Year: {start_year}, End Year: {end_year}")

    # Calculate the 5-year moving average of the temperature
    data['Moving_Avg'] = data['TEMPERATURE'].rolling(window=5).mean()

    # Create a plot with a secondary y-axis for the Moving Average
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot the TEMPERATURE data (Primary Y-axis)
    ax1.plot(data['Year'], data['TEMPERATURE'], label='Temperature', color='blue')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Temperature (°C)', color='blue')
    ax1.set_ylim(0, data['TEMPERATURE'].max() * 1.1)  # Scaling the Y-axis by 10%
    ax1.tick_params(axis='y', labelcolor='blue')
    
    # Plot the Moving Average data (Secondary Y-axis)
    ax2 = ax1.twinx()
    ax2.plot(data['Year'], data['Moving_Avg'], label='5-Year Moving Avg', color='green')
    ax2.set_ylabel('5-Year Moving Average', color='green')
    ax2.set_ylim(0, data['Moving_Avg'].max() * 1.1)  # Scaling the Y-axis by 10%
    ax2.tick_params(axis='y', labelcolor='green')

    # Title and grid
    plt.title(f'Yearly Temperature and 5-Year Moving Average ({start_year} - {end_year})')
    ax1.grid(True)

    # Add legends
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # Save the plot as an image in the static folder
    plot_path = "static/temperature_moving_avg_plot.png"
    plt.savefig(plot_path)
    plt.close()

    return plot_path


# Route for the main page to display the plot
@app.route('/')
def index():
    plot_path = generate_plot()
    return render_template('index-moving-avg.html', plot_path=plot_path)

# Route to serve the plot image from the 'static' folder
@app.route('/static/<path:filename>')
def serve_plot(filename):
    return send_from_directory('static', filename)

# Run the app on port 8080
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
