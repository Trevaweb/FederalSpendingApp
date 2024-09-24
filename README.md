# Spending Analysis Project

This project is a web application built with Flask and PySpark that fetches federal spending data, processes it, and visualizes the top and bottom spending entities.

## Features

- Fetches spending data from the USA Spending API.
- Processes data using PySpark for efficient handling of large datasets.
- Visualizes the top 10 highest and lowest spending entities using Matplotlib.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/spending-analysis.git
   ```
2. Navigate to the project directory:
   ```bash
   cd spending-analysis
   ```
3. Set up a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
5. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python src/app.py
   ```
2. Open your web browser and go to `http://127.0.0.1:5000/`.
3. Enter the fiscal year and quarter to fetch and visualize spending data.

## Data Storage

The application saves fetched data in JSON and CSV formats in a `data` directory, organized by fiscal year and quarter.

## Visualization

The application generates bar plots for the top 10 highest and lowest spending entities, saved in the `static` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
