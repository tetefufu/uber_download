from datetime import datetime, timedelta


def get_latest_monday():
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    latest_monday = datetime(monday.year, monday.month, monday.day)
    return latest_monday


def generate_dates_rolling_30():
    now = datetime.now()

    # Calculate tomorrow's date at midnight
    tomorrow_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the date 30 days before tomorrow's date
    from_date = (tomorrow_midnight - timedelta(days=30))

    # Format the dates in the desired format
    from_date_str = from_date.strftime("%Y-%m-%dT%H:%M:%S.000+04:00")
    end_date_str = tomorrow_midnight.strftime("%Y-%m-%dT%H:%M:%S.000+04:00")

    return from_date_str, end_date_str

