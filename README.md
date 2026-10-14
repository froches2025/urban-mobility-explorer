# Urban Mobility Data Explorer
This repository contains an enterprise-level full-stack application designed to analyze and visualize the New York City Taxi Trip dataset. The system processes raw transit data, stores it in a normalized relational database, and serves it through a backend API to an interactive frontend dashboard.

### Team Task Sheet
[https://docs.google.com/spreadsheets/d/1JR4F3T7Er_94yCupQfcRhtoRWShdTGLvrSVvKbx0MW8/edit?usp=sharing](https://docs.google.com/spreadsheets/d/1JR4F3T7Er_94yCupQfcRhtoRWShdTGLvrSVvKbx0MW8/edit?usp=sharing)

### Demo Video
https://youtube.com/placeholder

## System Architecture
The application is built with a clear separation of concerns, utilizing a three-tier architecture:
- Data Pipeline & Database (SQLite): Python scripts process raw .parquet and .csv files, handle missing values, calculate derived features, and seed a normalized SQLite database.
- Backend API (Python/Flask): A RESTful API that interfaces with the database, handling dynamic queries and executing custom spatial mathematics.
- Frontend Dashboard (HTML/CSS/JS): A vanilla JavaScript and HTML frontend utilizing modular components to render interactive data visualizations (Chart.js) and filterable tables.

## Project Structure
```
urban-mobility-explorer/
├── README.md
├── backend/
│   ├── db.py                  # SQLite connection and query execution utilities
│   ├── main.py                # Flask application and API route definitions
│   └── spatial_utils.py       # Custom Haversine spatial filtering algorithm
├── codevibe-reports/          # Team AI authorship and ownership verification files
│   ├── favour_summative-urban-mobility-analytics.report.json
│   ├── hussaina_summative-urban-mobility-analytics.report.json
│   └── urban-mobility-explorer.report.json
├── data-pipeline/
│   ├── raw_data               # TLC datasets (taxi_zone_lookup.csv, etc.)
│   │   └── taxi_zone_lookup.csv
│   ├── schema.sql             # Database normalization and table definitions
│   ├── scripts/               # Python scripts for data cleaning (clean_data.py)
│   │   ├── __pycache__
│   │   │   └── clean_data.cpython-312.pyc
│   │   └── clean_data.py
│   └── seed_db.py             # SQLite database population script
├── docs/                      # PDF architecture and insight documentation
└── frontend/
    ├── index.html             # Dashboard entry point
    └── src/
        ├── components/        # UI modules (charts.js, tripTable.js)
        │   ├── charts.js
        │   └── tripTable.js
        ├── main.js            # Frontend initialization
        ├── services/          # API interaction logic (api.js)
        │   └── api.js
        └── styles/            # CSS stylesheets (main.css)
            └── main.css

13 directories, 18 files
```
## Setup and Installation
1. **Database Initialization**
Ensure you have Python 3.x installed. Navigate to the data pipeline directory to prepare the database.
```
cd data-pipeline
# Run the cleaning and seeding scripts (ensure raw datasets are in /raw_data)
python scripts/clean_data.py
python seed_db.py
```

*Note: This will generate the taxi_data.db SQLite file used by the backend.*

2. **Backend Server Execution**
Navigate to the backend directory, install the required dependencies, and start the Flask server.
```
cd ../backend
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install requirements
pip install flask flask-cors

# Run the API server
python main.py
```

The backend will run on [http://127.0.0.1:5000](http://127.0.0.1:5000).

3. **Frontend Dashboard Launch**
Because the frontend uses vanilla HTML/JS, you can serve it using a simple local server to avoid CORS issues.
```
cd ../frontend
# Start a basic Python HTTP server
python -m http.server 8080
```

Open your browser and navigate to http://localhost:8080 to interact with the dashboard.

## API Reference & Algorithmic Features
**Custom Data Structure/Algorithm (DSA):**
The backend includes a manual implementation of the Haversine Formula (spatial_utils.py). This algorithm calculates the great-circle distance between two latitude/longitude points on a sphere in $O(N)$ time complexity, allowing the application to dynamically filter taxi zones within a custom coordinate radius without relying on external spatial database extensions or libraries.

- GET /api/trips: Retrieves filtered trip records. Accepts query parameters (min_fare, min_distance, time_range).
- GET /api/zones/nearby: Executes the custom Haversine algorithm. Accepts lat, lon, and radius parameters to return spatially filtered transit zones.