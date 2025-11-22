from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

def parse_muc_schedule(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Get the initial date from the main header
    # Example: "Flights to Munich on 22.11.2025"
    header = soup.find('h3', class_='fp-flights-headline')
    current_date_str = None
    if header:
        # Regex to extract DD.MM.YYYY
        match = re.search(r'(\d{2}\.\d{2}\.\d{4})', header.get_text())
        if match:
            current_date_str = match.group(1)

    # 2. Target the specific table
    table = soup.find('table', class_='fp-flights-table-large')
    if not table:
        return pd.DataFrame()

    # 3. Iterate over ALL rows in the tbody (recursive=False to avoid nested tables)
    # We need both 'fp-flight-item' (data) AND 'fp-flight-date' (date separators)
    tbody = table.find('tbody')
    all_rows = tbody.find_all('tr', recursive=False)
    
    flights_data = []

    for row in all_rows:
        classes = row.get('class', [])
        
        # --- Case A: It is a Date Separator Row ---
        # Example: <tr class="fp-flight-date">...Flights to Munich on 23.11.2025...</tr>
        if 'fp-flight-date' in classes:
            text = row.get_text()
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                current_date_str = match.group(1)
            continue # Move to next row, no flight data here

        # --- Case B: It is a Flight Data Row ---
        # Example: <tr class="fp-flight-item">...</tr>
        if 'fp-flight-item' in classes:
            try:
                # Get Flight Number
                flight_num = row.find('td', class_='fp-flight-number').get_text(strip=True)

                # Get Time Info
                # Example text: "22:25 |" or "06:45 | 06:30"
                time_cell = row.find('td', class_='fp-flight-time-muc').get_text(strip=True)

                final_time_str = "" # Renamed variable for clarity

                if '|' in time_cell:
                    parts = time_cell.split('|')
                    
                    # Check if the second part (Expected Time) is present and not just empty whitespace
                    expected_time = parts[1].strip() if len(parts) > 1 else ""

                    if expected_time:
                        # 1. Expected time is available (e.g., "06:30")
                        final_time_str = expected_time
                    else:
                        # 2. Expected time is missing, so use the Scheduled Time (e.g., "22:25 |")
                        final_time_str = parts[0].strip()
                        
                else:
                    # 3. Only a single time value is present (no pipe)
                    final_time_str = time_cell.strip()
                
                # Combine Date and Time into ISO Format
                iso_string = None
                if current_date_str and final_time_str:
                    # Input format: Date "22.11.2025", Time "22:25"
                    dt_obj = datetime.strptime(
                        f"{current_date_str} {final_time_str}", 
                        "%d.%m.%Y %H:%M"
                    )
                    iso_string = dt_obj.isoformat()

                flights_data.append({
                    'flight_num': flight_num,
                    "expected_time": iso_string,
                })

            except (AttributeError, ValueError):
                continue

    return pd.DataFrame(flights_data)

# Usage Example (assuming 'html_content' is loaded)
# df = parse_muc_schedule_iso(fullContent)
# print(df.head())