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
    