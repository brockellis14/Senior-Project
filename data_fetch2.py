import requests
import json

# USGS API URL for Idaho rivers
url = "https://waterservices.usgs.gov/nwis/iv/?format=json&stateCd=wa&siteStatus=all&siteType=ST"

# Send request to the API
response = requests.get(url)
data = response.json()

# Prepare data for the JavaScript map
map_data2 = []
time_series = data.get('value', {}).get('timeSeries', [])

# Loop through each site in the timeSeries data
for site in time_series:
    site_name = site['sourceInfo']['siteName']
    latitude = site['sourceInfo']['geoLocation']['geogLocation']['latitude']
    longitude = site['sourceInfo']['geoLocation']['geogLocation']['longitude']

    # Loop through each 'values' object to get the streamflow data
    for value_item in site.get('values', []):
        for value in value_item.get('value', []):
            streamflow = value.get('value')
            date_time = value.get('dateTime')

            # Only append if the streamflow data is not missing
            if streamflow and date_time:
                map_data2.append({
                    "site_name": site_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "streamflow": streamflow,
                    "date_time": date_time
                })

# Write the data into a JavaScript file as a JS variable
with open('map_data2.js', 'w') as js_file:
    js_file.write(f"const mapData = {json.dumps(map_data2)};")
