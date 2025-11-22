import json
from datetime import datetime
import os # To check if the file exists

TIME_SERIES_FILE = "price_estimates_series.json"

def add_to_series(m5_est: float, m6_est: float):
    """
    Creates the JSON file if it doesn't exist, and appends a new entry 
    with the current datetime and the two estimates.
    """
    
    # 1. Prepare the new data entry
    timestamp = datetime.now().isoformat()
    new_entry = {
        "timestamp": timestamp,
        "market5_estimate": m5_est,
        "market6_estimate": m6_est
    }

    # 2. Check if file exists and load existing data or initialize new data
    data = []
    if os.path.exists(TIME_SERIES_FILE):
        try:
            with open(TIME_SERIES_FILE, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # Handle empty or invalid JSON file by starting fresh
            print(f"Warning: Could not decode JSON from {TIME_SERIES_FILE}. Starting new series.")
            data = []
    
    # 3. Append the new entry
    data.append(new_entry)
    
    # 4. Write all data back to the file
    try:
        with open(TIME_SERIES_FILE, 'w') as f:
            # Use indent for readability in the file
            json.dump(data, f, indent=4)
        print(f"Successfully appended new data point to {TIME_SERIES_FILE}")
    except Exception as e:
        print(f"Error writing to file {TIME_SERIES_FILE}: {e}")