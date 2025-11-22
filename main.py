from src.fetch.main import fetch_schedule
from src.indicators.markets import price5, price6

arrivals = fetch_schedule(is_arrival=True)
departures = fetch_schedule(is_arrival=False)

print("Estimate 5:", price5(arrivals, departures))
print("Estimate 6:", price6(arrivals, departures))