from datetime import datetime
import logging
import os
import asyncio
import csv
import uuid

import requests

from utils.config_utils import read_config
from utils.creds import extract_cookie_value_yango
from urllib.parse import quote

from utils.date_utils import generate_dates_rolling_30
from utils.file_utils import save_file
from utils.format_utils import convert_to_dict_list
from utils.log_utils import *
from utils.yango_client import YangoClient

cookie_str = extract_cookie_value_yango()
config = read_config("config.yml")
client = YangoClient(cookie_str=cookie_str)

def save_csv_content(url, filename):
    response = requests.get(url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        csv_content = list(reader)

    return csv_content

async def start_report_generation(report, start_date, end_date):
    operation_id = uuid.uuid4().hex
    if report == "payouts":
        await client.get_payouts(operation_id, start_date, end_date)
    else:
        await client.get_transactions(operation_id, start_date, end_date)
    return operation_id

async def wait_for_report_completion(operation_id):
    status = "new"
    while status not in ("uploaded", "completed"):
        await asyncio.sleep(5)
        status = (await client.get_report_status(operation_id)).get("status")
    return status

async def fetch_report_download_url(operation_id):
    return await client.download_report(operation_id)


def download_and_parse_csv(download_url, filename):
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename)
    logging.info(f"{full_path=}")
    logging.info(f"{base_path=}")

    os.makedirs(base_path, exist_ok=True)

    return save_csv_content(download_url, full_path)


async def fetch_transaction_details(client, transaction):
    order_id = transaction.get("Order ID")
    driver_profile_id = transaction.get("Driver ID")
    if order_id and driver_profile_id and len(order_id) > 10 and len(driver_profile_id) > 10:
        detail = await client.get_order_details(order_id, driver_profile_id, tz="Asia/Dubai")
        return transaction | detail
    return transaction

async def get_all_transaction_details(client, transactions):
    tasks = [fetch_transaction_details(client, transaction) for transaction in transactions]
    transactions_details = await asyncio.gather(*tasks)
    return transactions_details


async def main():
    start_date, end_date = generate_dates_rolling_30(config.get("yango_start_from", 60))
    operation_id = await start_report_generation("transactions", start_date, end_date)
    await wait_for_report_completion(operation_id)
    report_details = await fetch_report_download_url(operation_id)
    download_url = report_details.get("link")
    filename = report_details.get("file_name")
    csv_content = download_and_parse_csv(download_url, filename)
    logging.info("CSV content downloaded and parsed successfully.")
    
    transactions = convert_to_dict_list(csv_content)
    transactions_details = await get_all_transaction_details(client, transactions)

    logging.info("CSV content downloaded and parsed successfully.")

    filename = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M')}_yango_downloader"
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename) + ".csv"
    save_file(transactions_details, full_path)

    operation_id = await start_report_generation("payouts", start_date, end_date)
    await wait_for_report_completion(operation_id)
    report_details = await fetch_report_download_url(operation_id)
    download_url = report_details.get("link")
    filename = report_details.get("file_name")
    csv_content = download_and_parse_csv(download_url, filename)
    payouts = convert_to_dict_list(csv_content)

    filename = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M')}_yango_downloader_payouts"
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename) + ".csv"
    save_file(payouts, full_path)
    
    return transactions_details


if __name__ == "__main__":
    asyncio.run(main())
