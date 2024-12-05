import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_file
import glob

# Initialize Flask app
app = Flask(__name__)

# Create 'static' directory if not exists
if not os.path.exists('static'):
    os.makedirs('static')

# Helper function to generate plots from CSV data
def generate_plot(folder_path):
    # Get all CSV files in the folder that match the pattern "yearly-<calc_logic>.csv"
    csv_files = glob.glob(os.path.join(folder_path, 'yearly-*.csv'))
    if not csv_files:
        return None  # No matching CSV files found
    
    plot_paths = []  # List to hold paths of generated plots

    for csv_file in csv_files:
        # Read CSV data into pandas DataFrame
        try:
            data = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
            continue
        
        # Print columns for debugging
        print(f"Processing {csv_file} with columns: {data.columns}")

        # Calculate the 5-year moving average of the temperature
        data['5-Year Moving Avg'] = data['TEMPERATURE'].rolling(window=5).mean()

        # Determine the dynamic range for the X-axis based on the years
        min_year = data['Year'].min()
        max_year = data['Year'].max()

        # Create the plot for the temperature and moving average
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot Temperature
        ax1.plot(data['Year'], data['TEMPERATURE'], label='Temperature', color='blue')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Temperature (°C)', color='blue')
        ax1.set_ylim(data['TEMPERATURE'].min() * 0.9, data['TEMPERATURE'].max() * 1.1)  # Scale Y-axis by 10%
        ax1.tick_params(axis='y', labelcolor='blue')

        # Plot 5-Year Moving Average
        ax2 = ax1.twinx()
        ax2.plot(data['Year'], data['5-Year Moving Avg'], label='5-Year Moving Avg', color='red')
        ax2.set_ylabel('5-Year Moving Average', color='red')
        ax2.set_ylim(data['5-Year Moving Avg'].min() * 0.9, data['5-Year Moving Avg'].max() * 1.1)  # Scale Y-axis by 10%
        ax2.tick_params(axis='y', labelcolor='red')

        # Set the title and grid
        plt.title(f"Yearly Temperature and 5-Year Moving Average ({min_year} - {max_year})")
        ax1.grid(True)

        # Add legends
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        # Save the plot as an image
        plot_path = f"static/{os.path.basename(csv_file).replace('.csv', '-plot.png')}"
        plt.savefig(plot_path)
        plt.close()

        plot_paths.append(plot_path)  # Add the plot path to the list

    return plot_paths  # Return a list of plot paths

# Route to handle the main page and display plots
@app.route('/')
def index():
    # Specify the folder path containing the CSV files (adjust as needed)
    folder_path =  'data/19640101-20231231'
    
    plot_paths = generate_plot(folder_path)
    
    if not plot_paths:
        return "No data found to generate plots.", 404
    
    # Render the index page and pass the plot paths for each file
    return render_template('index-moving-avg.html', plot_paths=plot_paths)

# Route to send the plot image as a response

@app.route('/static/<plot_filename>')
def plot(plot_filename):
    plot_path = f"static/{plot_filename}"
    return send_file(plot_path, mimetype='image/png')

# Run the Flask app on port 8080
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
