import requests
import json
import time
import traceback

# Base URL for NWPS API
base_url = "https://api.water.noaa.gov/nwps/v1"

# Function to fetch a list of all gauges
def fetch_gauge_data(params, max_retries=5, retry_delay=5):
    gauges_url = f"{base_url}/gauges"
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch gauge data...")
            response = requests.get(gauges_url, params=params, timeout=30)
            response.raise_for_status()
            
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

# Function to fetch stageflow data for a specific gauge
def fetch_flow_data(gauge_id, max_retries=5, retry_delay=5):
    stageflow_url = f"{base_url}/gauges/{gauge_id}/stageflow"
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch flow data for gauge {gauge_id}...")
            response = requests.get(stageflow_url, timeout=30)
            response.raise_for_status()
            
            # Successful response
            print(f"Flow data for gauge {gauge_id} fetched successfully.")
            return response.json()
        
        except requests.Timeout:
            print(f"Request for gauge {gauge_id} timed out. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        
        except requests.RequestException as http_err:
            print(f"HTTP error occurred: {http_err}")
            break
        
        except Exception as err:
            print(f"An error occurred: {err}")
            break
    
    print(f"Failed to fetch flow data for gauge {gauge_id} after {max_retries} attempts.")
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

# Process the gauge data if successfully fetched
if gauges_data is not None:
    map_data = []  # List to store map data for JavaScript

    for gauge in gauges_data.get('gauges', []):
        gauge_id = gauge['lid']
        gauge_name = gauge['name']
        latitude = gauge['latitude']
        longitude = gauge['longitude']
        print(f"Fetching flow data for gauge: {gauge_name} (ID: {gauge_id})")

        try:
            # Fetch flow data for the specific gauge using its identifier
            flow_data = fetch_flow_data(gauge_id)

            if flow_data:
                observed = flow_data.get('status', {}).get('observed', {})
                forecast = flow_data.get('status', {}).get('forecast', {})

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
            else:
                print(f"Failed to fetch flow data for gauge {gauge_id}")

        except Exception as e:
            print(f"Error processing gauge {gauge_name} (ID: {gauge_id}): {str(e)}")
            traceback.print_exc()  # Print the full stack trace for debugging

    # Save the map data into a JavaScript file for your map
    with open('map_data.js', 'w') as js_file:
        js_file.write(f"const mapData = {json.dumps(map_data, indent=2)};")
    print("map_data.js file created successfully.")

else:
    print("No gauge data available to process.")
