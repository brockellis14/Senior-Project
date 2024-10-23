import requests
import json
import time
import traceback

# Base URL for NWPS API
base_url = "https://api.water.noaa.gov/nwps/v1"
base_url_stageflow = "https://api.water.noaa.gov/nwps/v1/gauges/stageflow"

# Function to fetch gauge data with retry mechanism and timeout handling
def fetch_gauge_data(params, max_retries=5, retry_delay=5):
    """
    Fetch gauge data with retry mechanism and timeout handling.
    :param params: Dictionary of parameters (bounding box, etc.)
    :param max_retries: Maximum number of retries before giving up
    :param retry_delay: Time in seconds to wait before retrying
    :return: JSON response if successful, None otherwise
    """
    gauges_url = f"{base_url}/gauges"
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch gauge data...")
            response = requests.get(gauges_url, params=params, timeout=30)
            response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
            
            # Successful response
            print("Gauge data fetched successfully.")
            return response.json()
        
        except requests.Timeout:
            print(f"Request timed out. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        
        except requests.RequestException as http_err:
            print(f"HTTP error occurred: {http_err}")
            break
        
        except Exception as err:
            print(f"An error occurred: {err}")
            break
    
    print(f"Failed to fetch gauge data after {max_retries} attempts.")
    return None

# Function to fetch stageflow data for all gauges in a single request
def fetch_all_stageflow_data(max_retries=5, retry_delay=5):
    """
    Fetch stageflow data for all gauges with retry mechanism and timeout handling.
    :param max_retries: Maximum number of retries before giving up
    :param retry_delay: Time in seconds to wait before retrying
    :return: JSON response if successful, None otherwise
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch stageflow data for all gauges...")
            response = requests.get(base_url_stageflow, timeout=30)
            response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
            
            # Successful response
            print("Stageflow data fetched successfully.")
            return response.json()
        
        except requests.Timeout:
            print(f"Request timed out. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        
        except requests.RequestException as http_err:
            print(f"HTTP error occurred: {http_err}")
            break
        
        except Exception as err:
            print(f"An error occurred: {err}")
            break
    
    print(f"Failed to fetch stageflow data after {max_retries} attempts.")
    return None

# Set parameters for a specific geographical bounding box (adjust to your needs)
params = {
    "bbox.xmin": -125.0,  # Example bounding box coordinates
    "bbox.ymin": 45.0,
    "bbox.xmax": -110.0,
    "bbox.ymax": 50.0,
    "srid": "EPSG_4326"  # WGS84 - standard GPS
}

# Fetch the gauge data
gauges_data = fetch_gauge_data(params)

# Fetch stageflow data for all gauges
stageflow_data = fetch_all_stageflow_data()

# Process the gauge and stageflow data if successfully fetched
if gauges_data is not None and stageflow_data is not None:
    map_data = []  # List to store map data for JavaScript

    # Create a dictionary to easily look up stageflow data by gauge ID
    stageflow_lookup = {gauge['lid']: gauge for gauge in stageflow_data.get('gauges', [])}

    for gauge in gauges_data.get('gauges', []):
        gauge_id = gauge['lid']
        gauge_name = gauge['name']
        latitude = gauge['latitude']
        longitude = gauge['longitude']
        print(f"Processing data for gauge: {gauge_name} (ID: {gauge_id})")

        try:
            # Fetch stageflow data for the specific gauge
            stageflow = stageflow_lookup.get(gauge_id, {})

            # If stageflow data exists, get observed and forecast data
            observed = stageflow.get('status', {}).get('observed', {})
            forecast = stageflow.get('status', {}).get('forecast', {})

            # Append data to map_data list
            map_data.append({
                "site_name": gauge_name,
                "latitude": latitude,
                "longitude": longitude,
                "observed_flow": observed.get('primary', 'N/A'),
                "forecast_flow": forecast.get('primary', 'N/A'),
                "unit": observed.get('primaryUnit', 'N/A'),
                "observed_time": observed.get('validTime', 'N/A'),
                "forecast_time": forecast.get('validTime', 'N/A')
            })

        except Exception as e:
            print(f"Error processing gauge {gauge_name} (ID: {gauge_id}): {str(e)}")
            traceback.print_exc()  # Print the full stack trace for debugging

    # Save the map data into a JavaScript file for your map
    with open('map_data.js', 'w') as js_file:
        js_file.write(f"const mapData = {json.dumps(map_data, indent=2)};")
    print("map_data.js file created successfully.")

else:
    print("No gauge or stageflow data available to process.")
