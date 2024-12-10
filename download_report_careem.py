import asyncio
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


async def get_trips_sync(drivers):
    driver_trips = []
    for driver in drivers:
        for number in range(config['report_start_from']):
            driver_trips.extend(await client.get_trips(driver, number))

    return driver_trips


async def get_trips_async(drivers):
    tasks = [
        client.get_trips(driver, number)
        for driver in drivers
        for number in range(config['report_start_from'])
    ]
    
    results = await asyncio.gather(*tasks)

    driver_trips = [trip for result in results for trip in result]
    return driver_trips


async def get_trips_details_sync(trips):
    driver_trips = []
    for trip in trips:
        driver_trips.append(await client.get_trip_detail(trip))

    return driver_trips


async def get_trips_details_async(trips):
    tasks = [client.get_trip_detail(trip) for trip in trips]
    driver_trips = await asyncio.gather(*tasks)

    return driver_trips


def save_file(list_of_dicts, filepath):
    logging.info(f"saving {filepath}")
    if not list_of_dicts:
        raise ValueError("The list of dictionaries is empty.")

    header = []
    seen_keys = set()

    for dictionary in list_of_dicts:
        for key in dictionary.keys():
            if key not in seen_keys:
                header.append(key)
                seen_keys.add(key)


    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(list_of_dicts)
    logging.info(f"saved to file {filepath}")


async def main():
    captain_ids = await get_captain_ids()
    trips = await get_trips_async(captain_ids)
    trips_details = await get_trips_details_async(trips)

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M')}_careem_downloader"
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename) + ".csv"
    save_file(trips_details, full_path)


if __name__ == "__main__":
    asyncio.run(main())
    