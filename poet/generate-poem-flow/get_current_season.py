from promptflow import tool
import ntplib
from datetime import datetime, timezone

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need

def parse_season_from_date(date):
    """Determine the season based on the date."""
    month = date.month
    day = date.day

    # technically this only works for the northern hemisphere. oops! we can fix this later. -mgb
    
    if (month == 12 and day >= 21) or (month in [1, 2]) or (month == 3 and day < 20):
        return 'Winter'
    elif (month == 3 and day >= 20) or (month in [4, 5]) or (month == 6 and day < 21):
        return 'Spring'
    elif (month == 6 and day >= 21) or (month in [7, 8]) or (month == 9 and day < 23):
        return 'Summer'
    elif (month == 9 and day >= 23) or (month in [10, 11]) or (month == 12 and day < 21):
        return 'Fall'
    return 'Unknown'

@tool
def get_season() -> str:

    client = ntplib.NTPClient()
    response = client.request('time.windows.com')
    current_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
    season = parse_season_from_date(current_time)

    return season