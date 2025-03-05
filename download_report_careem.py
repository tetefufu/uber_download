import asyncio
from datetime import datetime
import os

from utils.careem_client import CareemClient
from utils.config_utils import read_config
from utils.creds import extract_bearer_token

from utils.file_utils import save_file
from utils.log_utils import *
from asyncio import Semaphore

bearer_token = extract_bearer_token()
config = read_config("config.yml")
client = CareemClient(
    org_id=1, 
    start_from=config['report_start_from'], 
    bearer_token=bearer_token,
    delay=config.get('delay', 0)
)


async def get_captain_ids():
    captain_ids = await client.get_drivers()
    return captain_ids


async def get_trips_sync(drivers):
    driver_trips = []
    for driver in drivers:
        for number in range(config['report_start_from']):
            driver_trips.extend(await client.get_trips(driver, number))

    return driver_trips


async def get_trips_async(drivers, thread_count=1):
    semaphore = Semaphore(thread_count)

    async def limited_get_trips(driver, number):
        async with semaphore:
            return await client.get_trips(driver, number)

    tasks = [
        limited_get_trips(driver, number)
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


async def get_trips_details_async(trips, thread_count=1):
    semaphore = Semaphore(thread_count)

    async def limited_get_trip_detail(trip):
        async with semaphore:
            return await client.get_trip_detail(trip)

    tasks = [limited_get_trip_detail(trip) for trip in trips]
    driver_trips = await asyncio.gather(*tasks)

    return driver_trips


async def main():
    captain_ids = await get_captain_ids()
    trips = await get_trips_async(captain_ids, thread_count=config.get("threads", 10))
    trips_details = await get_trips_details_async(trips, thread_count=config.get("threads", 10))

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M')}_careem_downloader"
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename) + ".csv"
    save_file(trips_details, full_path)


if __name__ == "__main__":
    asyncio.run(main())
    