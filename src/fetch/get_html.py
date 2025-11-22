import time
import requests

def get_muc_schedule(page, is_arrival: bool):
    base_url = f"https://www.munich-airport.com/flightsearch/{"arrivals" if is_arrival else "departures"}"

    # Construct the query parameters exactly as seen in your example request
    params = {
        'from': "2025-11-22T00:00:00",
        'allow_scroll_back': '1',
        'per_page': '50',
        'min_date': "2025-11-22T00:00:00",
        'max_date': "2025-11-24T00:00:00",
        'page': str(page),
        '_': str(int(time.time() * 1000))
    }

    # Headers are CRITICAL. Without 'User-Agent', the firewall will block you.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest', # Often required for AJAX endpoints
        'Referer': 'https://www.munich-airport.com/flights/arrivals'
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error: Status Code {response.status_code}")
            return ""
            
    except Exception as e:
        print(f"Request failed: {e}")
        return ""