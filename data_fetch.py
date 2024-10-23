import requests
import json
import time
import traceback

# Base URLs for NOAA and USGS APIs
noaa_base_url = "https://api.water.noaa.gov/nwps/v1"
usgs_url = "https://waterservices.usgs.gov/nwis/iv/"

# Function to fetch gauge data from NOAA API
def fetch_noaa_gauge_data(params, max_retries=5, retry_delay=5):
    gauges_url = f"{noaa_base_url}/gauges"
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch NOAA gauge data...")
            response = requests.get(gauges_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Successful response
            print("NOAA gauge data fetched successfully.")
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
    
    print(f"Failed to fetch NOAA gauge data after {max_retries} attempts.")
    return None


# Function to fetch flow data for a specific gauge from NOAA
def fetch_noaa_flow_data(gauge_id, max_retries=5, retry_delay=5):
    stageflow_url = f"{noaa_base_url}/gauges/{gauge_id}/stageflow"
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch NOAA flow data for gauge {gauge_id}...")
            response = requests.get(stageflow_url, timeout=30)
            response.raise_for_status()
            
            # Successful response
            print(f"NOAA flow data for gauge {gauge_id} fetched successfully.")
            return response.json()
        
        except requests.Timeout:
            print(f"Request for NOAA gauge {gauge_id} timed out. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        
        except requests.RequestException as http_err:
            print(f"HTTP error occurred: {http_err}")
            break
        
        except Exception as err:
            print(f"An error occurred: {err}")
            break
    
    print(f"Failed to fetch NOAA flow data for gauge {gauge_id} after {max_retries} attempts.")
    return None


# Function to fetch gauge data from USGS API
def fetch_usgs_gauge_data(params, max_retries=5, retry_delay=5):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to fetch USGS gauge data...")
            response = requests.get(usgs_url, params=params, timeout=30)
            response.raise_for_status()

            # Successful response
            print("USGS gauge data fetched successfully.")
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

    print(f"Failed to fetch USGS gauge data after {max_retries} attempts.")
    return None

# Helper function to find if a location already exists in map_data
def find_existing_location(map_data, latitude, longitude):
    for entry in map_data:
        if entry['latitude'] == latitude and entry['longitude'] == longitude:
            return entry
    return None

# Set parameters for fetching USGS gauge data (specifically for Idaho)
usgs_params = {
    "format": "json",
    "stateCd": "id",      # State code for Idaho
    "siteStatus": "active",
    "siteType": "ST"      # Site type: Stream gauge (ST)
}

# Set parameters for NOAA (example bounding box)
noaa_params = {
    "bbox.xmin": -125.0,  # Example bounding box coordinates
    "bbox.ymin": 45.0,
    "bbox.xmax": -110.0,
    "bbox.ymax": 50.0,
    "srid": "EPSG_4326"  # WGS84 - standard GPS
}

# Fetch NOAA and USGS gauge data
noaa_gauges_data = fetch_noaa_gauge_data(noaa_params)
usgs_gauges_data = fetch_usgs_gauge_data(usgs_params)

# Processing data
map_data = []  # List to store map data for JavaScript

# Process NOAA data if available
if noaa_gauges_data is not None:
    for gauge in noaa_gauges_data.get('gauges', []):
        gauge_id = gauge['lid']
        gauge_name = gauge['name']
        latitude = gauge['latitude']
        longitude = gauge['longitude']
        print(f"Fetching flow data for NOAA gauge: {gauge_name} (ID: {gauge_id})")

        try:
            # Fetch flow data for the specific NOAA gauge
            flow_data = fetch_noaa_flow_data(gauge_id)

            if flow_data:
                observed = flow_data.get('status', {}).get('observed', {})
                forecast = flow_data.get('status', {}).get('forecast', {})

                # Check if location already exists
                existing_location = find_existing_location(map_data, latitude, longitude)

                if existing_location:
                    # Merge NOAA data with existing entry
                    existing_location['noaa_observed_flow'] = observed.get('primary', 'N/A')
                    existing_location['noaa_forecast_flow'] = forecast.get('primary', 'N/A')
                    existing_location['noaa_unit'] = observed.get('primaryUnit', 'N/A')
                    existing_location['noaa_observed_time'] = observed.get('validTime', 'N/A')
                    existing_location['noaa_forecast_time'] = forecast.get('validTime', 'N/A')
                else:
                    # Create a new entry
                    map_data.append({
                        "site_name": gauge_name,
                        "latitude": latitude,
                        "longitude": longitude,
                        "noaa_observed_flow": observed.get('primary', 'N/A'),
                        "noaa_forecast_flow": forecast.get('primary', 'N/A'),
                        "noaa_unit": observed.get('primaryUnit', 'N/A'),
                        "noaa_observed_time": observed.get('validTime', 'N/A'),
                        "noaa_forecast_time": forecast.get('validTime', 'N/A')
                    })
            else:
                print(f"Failed to fetch flow data for NOAA gauge {gauge_id}")

        except Exception as e:
            print(f"Error processing NOAA gauge {gauge_name} (ID: {gauge_id}): {str(e)}")
            traceback.print_exc()

# Process USGS data if available
if usgs_gauges_data is not None:
    for site in usgs_gauges_data.get('value', {}).get('timeSeries', []):
        gauge_id = site['sourceInfo']['siteCode'][0]['value']
        gauge_name = site['sourceInfo']['siteName']
        latitude = site['sourceInfo']['geoLocation']['geogLocation']['latitude']
        longitude = site['sourceInfo']['geoLocation']['geogLocation']['longitude']
        print(f"Processing flow data for USGS gauge: {gauge_name} (ID: {gauge_id})")

        try:
            # Extract observed flow data for USGS
            flow_data = site.get('value', {})
            observed_flow = flow_data.get('value', 'N/A')  # Handle missing value field safely
            unit = site['variable']['unit'].get('unitCode', 'N/A')  # Safely handle unitCode

            # Check if location already exists
            existing_location = find_existing_location(map_data, latitude, longitude)

            if existing_location:
                # Merge USGS data with existing entry
                existing_location['usgs_observed_flow'] = observed_flow
                existing_location['usgs_unit'] = unit
                existing_location['usgs_observed_time'] = flow_data.get('dateTime', 'N/A')
            else:
                # Create a new entry
                map_data.append({
                    "site_name": gauge_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "usgs_observed_flow": observed_flow,
                    "usgs_unit": unit,
                    "usgs_observed_time": flow_data.get('dateTime', 'N/A')
                })

        except Exception as e:
            print(f"Error processing USGS gauge {gauge_name} (ID: {gauge_id}): {str(e)}")
            traceback.print_exc()

# Save the map data into a JavaScript file for your map
with open('map_data.js', 'w') as js_file:
    js_file.write(f"const mapData = {json.dumps(map_data, indent=2)};")
print("map_data.js file created successfully.")
