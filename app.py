from flask import Flask, render_template, request,  send_file
import folium
import requests
import json
import time
import numpy as np
import os

app = Flask(__name__)


@app.route('/routes')
def visualize_routes():
    # Your visualization code here
    map_object = folium.Map(location=[10, 10], zoom_start=5)
    # Save the map to a file
    map_object.save('templates/map.html')
    return render_template('map.html')

# Define your API URLs and keys

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
OSRM_API_URL = "http://router.project-osrm.org"
TOMTOM_API_KEY = "your_tomtom_api_key"
AQICN_API_KEY = "your_aqicn_api_key"

# Function to fetch route from OSRM
def fetch_route(start, end, retries=3):
    url = f"{OSRM_API_URL}/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
    params = {"overview": "full", "geometries": "geojson"}

    for attempt in range(retries):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print("OSRM API Response:", data)
            return data
        time.sleep(1)  # Wait before retrying

    return {"error": "Failed to fetch route data"}

# Function to fetch traffic data from TomTom
def fetch_traffic_data(lat, lon):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json"
    params = {
        "key": TOMTOM_API_KEY,
        "point": f"{lat},{lon}"
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to fetch air quality data from AQICN
def fetch_air_quality_data(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/"
    params = {"token": AQICN_API_KEY}
    response = requests.get(url, params=params)
    return response.json()

# Function to calculate emissions
def calculate_emissions(distance_km, fuel_rate, emission_factor):
    return distance_km * fuel_rate * emission_factor

# Validate coordinates
def is_valid_coordinate(coord):
    try:
        lat, lon = map(float, coord.split(","))
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except ValueError:
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Fetch user inputs
            start = request.form["start"]
            end = request.form["end"]
            fuel_rate = float(request.form["fuel_rate"])
            emission_factor = float(request.form["emission_factor"])

            # Validate inputs
            if not (is_valid_coordinate(start) and is_valid_coordinate(end)):
                return render_template("index.html", error="Invalid coordinates entered.")

            # Convert inputs to lat/lon
            start_coords = list(map(float, start.split(",")))
            end_coords = list(map(float, end.split(",")))

            # Fetch route data
            route_data = fetch_route(start_coords, end_coords)

            # Check if the response contains the required data
            if "routes" not in route_data or not route_data["routes"]:
                return render_template("index.html", error="Route data could not be fetched. Please try again.")

            route_geometry = route_data["routes"][0]["geometry"]["coordinates"]
            distance = route_data["routes"][0]["distance"] / 1000  # meters to km

            # Fetch additional data
            traffic_data = fetch_traffic_data(start_coords[0], start_coords[1])
            air_quality_data = fetch_air_quality_data(start_coords[0], start_coords[1])

            # Calculate emissions
            emissions = calculate_emissions(distance, fuel_rate, emission_factor)

            # Create map
            map_object = folium.Map(location=start_coords, zoom_start=12)
            folium.PolyLine([(coord[1], coord[0]) for coord in route_geometry], color="blue").add_to(map_object)
            map_html = map_object._repr_html_()

            return render_template(
                "result.html",
                map_html=map_html,
                distance=distance,
                emissions=emissions,
                traffic_data=traffic_data,
                air_quality_data=air_quality_data,
            )
        except Exception as e:
            return render_template("index.html", error=f"An error occurred: {e}")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
