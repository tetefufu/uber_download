from datetime import datetime, timedelta


def get_latest_monday():
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    latest_monday = datetime(monday.year, monday.month, monday.day)
    return latest_monday