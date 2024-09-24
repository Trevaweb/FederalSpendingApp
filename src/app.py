from flask import Flask, render_template, request
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, col, when, instr, expr
import requests
import json
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting
import matplotlib.pyplot as plt

app = Flask(__name__)

# Initialize Spark session
spark = SparkSession.builder.appName("Spending").getOrCreate()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fy = request.form['fy']
        quarter = request.form['quarter']
        
        # Create a directory for data if it doesn't exist
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Create a subdirectory for the specific FY and quarter
        subfolder = os.path.join(data_dir, f'fy{fy}_q{quarter}')
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        json_filename = os.path.join(subfolder, f'spending_data_fy{fy}_q{quarter}.json')
        csv_filename = os.path.join(subfolder, f'spending_data_fy{fy}_q{quarter}.csv')

        # Check if the JSON file exists
        if os.path.exists(json_filename):
            # Load data from the existing JSON file
            with open(json_filename, 'r') as json_file:
                spending_data = json.load(json_file)
        else:
            # Make the API call to fetch data
            url = "https://api.usaspending.gov/api/v2/spending/"
            params = {
                "limit": 1000,
                "page": 1,
                "type": "federal_account",
                "filters": {
                    "fy": fy,
                    "quarter": quarter,
                }
            }
            response = requests.post(url, json=params)
            if response.status_code == 200:
                spending_data = response.json().get('results', [])
                # Save the data to a JSON file for future use
                with open(json_filename, 'w') as json_file:
                    json.dump(spending_data, json_file, indent=4)
            else:
                return f"Error fetching data: {response.status_code} - {response.text}"

        # Convert JSON data to CSV using pandas
        df_pandas = pd.DataFrame(spending_data)
        df_pandas.to_csv(csv_filename, index=False)  # Save the DataFrame to a CSV file

        # Load the CSV file into a PySpark DataFrame
        df = spark.read.csv(csv_filename, header=True, inferSchema=True)

        # Clean and aggregate data
        df_cleaned = df.dropna()
        df_cleaned = df_cleaned.withColumn("amount", col("amount").cast("float"))

        # Group by name and sum the amounts
        df_grouped = df_cleaned.groupBy("name").agg(sum("amount").alias("total_spending"))

        # Clean names by removing everything after the first comma
        df_grouped = df_grouped.withColumn("name", 
            when(instr(col("name"), ",") > 0, 
                 expr("substring(name, 1, instr(name, ',') - 1)"))  # Keep everything before the first comma
            .otherwise(col("name"))  # Keep the original name if no comma
        )

        # Get the top 10 highest spending
        top_spending = df_grouped.orderBy(col("total_spending").desc()).limit(10)

        # Get the top 10 lowest spending, ignoring 0 or 0.0 values
        bottom_spending = df_grouped.filter(col("total_spending") > 0).orderBy(col("total_spending").asc()).limit(10)

        # Collect the data for visualization
        top_data = top_spending.collect()
        bottom_data = bottom_spending.collect()

        # Prepare data for plotting
        names_top = [row['name'] for row in top_data]
        total_spending_top = [row['total_spending'] for row in top_data]

        names_bottom = [row['name'] for row in bottom_data]
        total_spending_bottom = [row['total_spending'] for row in bottom_data]

        # Create a bar plot using Matplotlib
        plt.figure(figsize=(14, 8))  # Increase figure size

        # Plot top spending
        plt.subplot(1, 2, 1)  # 1 row, 2 columns, 1st subplot
        plt.bar(names_top, total_spending_top, color='red')
        plt.title('Top 10 Highest Spending')
        plt.xlabel('Name')
        plt.ylabel('Total Spending')
        plt.xticks(rotation=45, ha='right')  # Rotate x labels for better readability

        # Plot bottom spending
        plt.subplot(1, 2, 2)  # 1 row, 2 columns, 2nd subplot
        plt.bar(names_bottom, total_spending_bottom, color='blue')
        plt.title('Top 10 Lowest Spending (Excluding Zero)')
        plt.xlabel('Name')
        plt.ylabel('Total Spending')
        plt.xticks(rotation=45, ha='right')  # Rotate x labels for better readability

        # Adjust layout to make room for rotated labels
        plt.tight_layout()  # Automatically adjust subplot parameters
        plt.subplots_adjust(bottom=0.5, top=0.85)  # Adjust margins

        # Create a directory for static files if it doesn't exist
        static_dir = 'static'
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)

        # Save the plot as an image
        plt.savefig(os.path.join(static_dir, f'spending_chart_fy{fy}_q{quarter}.png'))  # Save the plot as an image
        plt.close()

        return render_template('spending.html', top_data=top_data, bottom_data=bottom_data, fy=fy, quarter=quarter)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
