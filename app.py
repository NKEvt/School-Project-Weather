from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def home():
    # Ensure the forecast file exists
    forecast_file = 'data/forecast_output.csv'
    if not os.path.exists(forecast_file):
        return "Forecast data not found. Please run the forecast script first."

    # Read the forecast data
    forecast_df = pd.read_csv(forecast_file)

    # Convert the DataFrame to HTML
    forecast_html = forecast_df.to_html(classes='table table-striped', index=False)

    return render_template('index.html', table=forecast_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
