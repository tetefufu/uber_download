from datetime import datetime
import logging
import os
import time
import aiohttp
import asyncio
import csv

import requests

from download_report_careem import save_file
from utils.config_utils import read_config
from utils.creds import extract_cookie_value_yango
from urllib.parse import quote

from utils.log_utils import *

class YangoClient:
    def __init__(self, cookie_str):
        self.headers = {
            "Cookie": cookie_str,
            # "Accept": "application/json, text/plain, */*",
            "Accept": "application/json",
            "X-Client-Version": "fleet/13631",
            "X-Park-Id": "c5cf968c4c2f4bbc947c8c0703b7e124",
            "sec-ch-ua-platform": "\"Windows\"",
            "Language": "en"
        }
        self.base_url = "https://fleet.yango.com/api"

    async def get_transactions(self, operation_id, from_date, to_date):
        url = f"{self.base_url}/v1/reports/transactions/park/download-async?operation_id={operation_id}"
        # url = "https://fleet.yango.com/api/v1/reports/transactions/park/download-async?operation_id=ba746b251a80468bb2c87bb87c607c96"
        # url = "https://fleet.yango.com/api/v1/reports/transactions/park/download-async?operation_id=ba746b251a80468bb2c87bb87c607c95"
        url = "https://fleet.yango.com/api/v1/reports/transactions/park/download-async?operation_id=ba746b251a80468bb2c87bb87c607c95"
        # url = f"{self.base_url}/v1/reports/transactions/park/download-async"
        
        # Prepare the request body
        payload = {
            "query": {
                "park": {
                    "transaction": {
                        "event_at": {
                            "from": from_date,
                            "to": to_date
                        },
                        "without_cash": True
                    }
                }
            },
            "charset": "utf-8-sig"
        }
        payload = '{"query":{"park":{"transaction":{"event_at":{"from":"2024-12-12T00:00:00.000+04:00","to":"2024-12-21T00:00:00.000+04:00"},"without_cash":true}}},"charset":"utf-8-sig"}'
        payload = '{"query":{"park":{"transaction":{"event_at":{"from":"2024-12-12T00:00:00.000+04:00","to":"2024-12-21T00:00:00.000+04:00"},"without_cash":true}}},"charset":"utf-8-sig"}'
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.post(url, data=payload) as response:  # Note: use 'data' to send raw JSON
                response.raise_for_status()
                return await response.json()

    async def get_payouts_list(self):
        url = f"{self.base_url}/fleet/fleet-payouts-web/v2/payouts/list"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_report_status(self, operation_id):
        url = f"{self.base_url}/fleet/reports-storage/v1/operations/status?operation_id={operation_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def download_report(self, operation_id):
        url = f"{self.base_url}/fleet/reports-storage/v1/operations/download?operation_id={operation_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_transactions_list(self):
        url = f"{self.base_url}/fleet/fleet-payouts-web/v1/transactions/list"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_order_details(self, order_id, driver_profile_id, tz="Asia/Dubai"):
        encoded_tz = quote(tz)
        url = f"{self.base_url}/fleet/fleet-orders/v1/orders/item/card?id={order_id}&tz={encoded_tz}&driver_profile_id={driver_profile_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.get(url) as response:
                response.raise_for_status()
                response_data = await response.json()

                transactions_info = response_data.get("transactions_info", {})

                flat_json = {}

                for group in transactions_info.get("groups", []):
                    group_name = group.get("name")
                    for transaction in group.get("transactions", []):
                        description = transaction.get("description")
                        event_at = transaction.get("event_at")
                        amount = transaction.get("amount")
                        
                        if description and event_at and amount:
                            key = f"{group_name}: {description}"
                            flat_json[key + "_amount"] = amount
                            flat_json[key + "_event_at"] = event_at

                return flat_json
            


            
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

async def start_report_generation():
    operation_id = "ba746b251a80468bb2c87bb87c607c96"
    await client.get_transactions("some_operation_id", "2024-12-12T00:00:00.000+04:00", "2024-12-22T00:00:00.000+04:00")
    return operation_id

async def wait_for_report_completion(operation_id):
    # operation_id = ""
    status = "new"
    while status not in ("uploaded", "completed"):
        await asyncio.sleep(5)
        status = (await client.get_report_status(operation_id)).get("status")
    return status

async def fetch_report_download_url(operation_id):
    return await client.download_report(operation_id)

def convert_to_dict_list(csv_list):
    columns = csv_list[0][0].split(';')
    
    result = []
    for row in csv_list[1:]:
        values = row[0].split(';')
        # Combine the column names with the values to create a dictionary
        row_dict = dict(zip(columns, values))
        row_dict['Order ID'] = row_dict.get('Document', '')[7:]
        result.append(row_dict)
    
    return result

def download_and_parse_csv(download_url, filename):
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename)

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
    operation_id = await start_report_generation()
    await wait_for_report_completion(operation_id)
    report_details = await fetch_report_download_url(operation_id)
    download_url = report_details.get("link")
    filename = report_details.get("file_name")

    if download_url and filename:
        csv_content = download_and_parse_csv(download_url, filename)
        logging.info("CSV content downloaded and parsed successfully.")
        
        transactions = convert_to_dict_list(csv_content)

        transactions_details = await get_all_transaction_details(client, transactions)

        filename = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M')}_yango_downloader"
        base_path = config['output_folder']
        full_path = os.path.join(base_path, filename) + ".csv"
        save_file(transactions_details, full_path)
        
        return transactions_details

    logging.error("Download URL or filename missing.")
    return []

if __name__ == "__main__":
    asyncio.run(main())
