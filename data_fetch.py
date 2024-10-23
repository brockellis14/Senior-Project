# Import necessary libraries at the top if not already done
import traceback

# Loop through the gauges to fetch data
for gauge in gauges_data.get('gauges', []):
    gauge_id = gauge['lid']
    gauge_name = gauge['name']
    latitude = gauge['latitude']
    longitude = gauge['longitude']
    print(f"Fetching flow data for gauge: {gauge_name} (ID: {gauge_id})")

    try:
        # Fetch flow data for the specific gauge
        flow_data = fetch_flow_data(gauge_id)

        if flow_data:
            observed = flow_data.get('status', {}).get('observed', {})
            forecast = flow_data.get('status', {}).get('forecast', {})

            # Add a print statement to log the fetched data for debugging
            print(f"Observed: {observed}, Forecast: {forecast}")

            # Process and save the data
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
        # Catch any exception and log it
        print(f"Error processing gauge {gauge_name} (ID: {gauge_id}): {str(e)}")
        traceback.print_exc()  # Print the full stack trace for debugging
