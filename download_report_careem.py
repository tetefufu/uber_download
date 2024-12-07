import asyncio
import aiohttp
import csv
from datetime import datetime
import logging
import os

from utils.careem_client import CareemClient
from utils.config_utils import read_config
from utils.creds import extract_bearer_token

from utils.log_utils import *

bearer_token = extract_bearer_token()
bearer_token = 'eyJraWQiOiI5ZWRhYzI2MC1iZGRiLTRiNjUtOTAxMi1mMmQ3MGUyNDJiYzYiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI2NTk3MzYwNSIsImF1ZCI6ImNvbS5jYXJlZW0uaW50ZXJuYWwiLCJsaW1vX3BvcnRhbFwvc291cmNlX2FwcCI6IkxJTU9fUE9SVEFMIiwiYWNjZXNzX3R5cGUiOiJDVVNUT01FUiIsInVzZXJfaWQiOjY1OTczNjA1LCJhenAiOiIyNjIyZDRhZi1lZGE0LTQyZWMtYTk1NC05NDdlMDk3NGY4MjEuc3VwcGxpZXIuY2FyZWVtLmNvbSIsImtpbmQiOiJDVVNUT01FUiIsInNjb3BlIjoib3BlbmlkIGVkZ2VfY2FwdGFpbiBwcm9maWxlIiwiaXNzIjoiaHR0cHM6XC9cL2lkZW50aXR5LmNhcmVlbS5jb21cLyIsImV4cCI6MTczMzU4NzI2MiwiaWF0IjoxNzMzNTAwODYyLCJqdGkiOiJjNGUzYmYxYi1mNmE5LTRkZWMtOTAxZS04YWY2ZjM3OTllMmIifQ.AxgVaOriZcVc2_Uron1v58qgI-3lQJdj6vFx6bl4v_ZZZROB4QIH_NFAd_koruafsomOWklmPJIu2LKCBuPrgiGEKNPCLtDX3QPtUq5ED2m3o6KVnYWhkpGYnvOnP9Kdw8JT-aFmRGzkQGkTG8FkDVHhJI9OvX3hrDiMu96gp4w6xv5KSSNBAH1HcGJuroEjfgeCtWiT6kRRLRfK5WzOtF8EfXsIY0IvBb-aMTz4uhfCvWql_Tht-J0pLdji0z-k668hZi0-QR_oQ0hkAl80O159zWGUtMgNJ8Don7HB44kp05Za01ctkHgXcwZ9cVhU6eDm6cSKqIuhfa6xau2Zpg'
config = read_config("config.yml")
client = CareemClient(org_id=1, start_from=config['report_start_from'], bearer_token=bearer_token)


async def get_captain_ids():
    captain_ids = await client.get_drivers()
    return captain_ids


async def get_trips(drivers):
    extended_trips = []
    
    driver_tasks = [client.get_trips(driver) for driver in drivers]
    driver_trips = await asyncio.gather(*driver_tasks)

    detail_tasks = []
    for driver, trips in zip(drivers, driver_trips):
        for trip in trips:
            task = client.get_trip_details(trip['transactionId'], driver)
            detail_tasks.append((trip, task))

    detail_results = await asyncio.gather(*[task for _, task in detail_tasks])

    for (trip, detail) in zip((t for trips in driver_trips for t in trips), detail_results):
        extended_trip = {**trip, **detail}
        extended_trips.append(extended_trip)

    return extended_trips


def save_file(list_of_dicts, filepath):
    logging.info(f"saving {filepath}")
    if not list_of_dicts:
        raise ValueError("The list of dictionaries is empty.")

    header = set()
    for dictionary in list_of_dicts:
        header.update(dictionary.keys())
    header = list(header)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(list_of_dicts)
    logging.info(f"saved to file {filepath}")


async def main():
    captain_ids = await get_captain_ids()
    trips = await get_trips(captain_ids)

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M')}_careem_downloader"
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename) + ".csv"
    save_file(trips, full_path)


if __name__ == "__main__":
    asyncio.run(main())
    