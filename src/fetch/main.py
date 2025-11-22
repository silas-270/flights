from src.fetch.extract_html import parse_muc_schedule
from src.fetch.get_html import get_muc_schedule

import pandas as pd

def fetch_schedule(is_arrival: bool):
    estimated_page_limit = 9
    all_schedules_dfs = []

    for i in range(estimated_page_limit):
        schedule_html = get_muc_schedule(i + 1, is_arrival=is_arrival)        
        schedule_df = parse_muc_schedule(schedule_html)

        if schedule_df is not None and not schedule_df.empty:
            all_schedules_dfs.append(schedule_df)

    if all_schedules_dfs:
        final_schedule_df = pd.concat(all_schedules_dfs, ignore_index=True)
        final_schedule_df['expected_time'] = pd.to_datetime(final_schedule_df['expected_time'])
        final_schedule_df = final_schedule_df.set_index('expected_time')
        final_schedule_df = final_schedule_df.sort_index()
        
        return final_schedule_df
    else:
        # Return an empty DataFrame if no data was fetched
        return pd.DataFrame()