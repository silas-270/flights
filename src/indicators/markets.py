import pandas as pd
import numpy as np

def price5(arrivals_df: pd.DataFrame, departures_df: pd.DataFrame):
    return 3 * (len(arrivals_df) + len(departures_df))

def price6(arrivals_df: pd.DataFrame, departures_df: pd.DataFrame):
    start_time = pd.Timestamp('2025-11-22 10:00:00')
    end_time_exclusive = pd.Timestamp('2025-11-23 10:00:00')

    # Filtern auf den relevanten Zeitraum
    arrivals_filtered = arrivals_df.loc[start_time:end_time_exclusive].copy()
    departures_filtered = departures_df.loc[start_time:end_time_exclusive].copy()

    arrivals_count = arrivals_filtered.resample('30min').count().iloc[:, 0].rename('Arrivals')
    departures_count = departures_filtered.resample('30min').count().iloc[:, 0].rename('Departures')

    data = pd.concat([arrivals_count, departures_count], axis=1).fillna(0)

    data['Arrivals'] = data['Arrivals'].astype(int)
    data['Departures'] = data['Departures'].astype(int)

    data['Sum'] = data['Arrivals'] + data['Departures']
    data['Diff'] = data['Arrivals'] - data['Departures']

    data['Metric'] = np.where(
        data['Sum'] > 0,
        300 * data['Diff'] / (data['Sum'] ** 1.5),
        0  # Wenn Summe 0 ist, ist die Metrik 0
    )

    total_metric_sum = data['Metric'].sum()
    settlement_value = round(total_metric_sum)

    return settlement_value