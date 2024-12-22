import aiohttp
import logging
from datetime import datetime
from urllib.parse import quote

class YangoClient:
    def __init__(self, cookie_str):
        self.headers = {
            "Cookie": cookie_str,
            "Accept": "application/json",
            "X-Client-Version": "fleet/13631",
            "X-Park-Id": "c5cf968c4c2f4bbc947c8c0703b7e124",
            "sec-ch-ua-platform": "\"Windows\"",
            "Language": "en"
        }
        self.base_url = "https://fleet.yango.com/api"

    async def get_transactions(self, operation_id, from_date, to_date):
        url = f"{self.base_url}/v1/reports/transactions/park/download-async?operation_id={operation_id}"
        
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
        
        # payload = '{"query":{"park":{"transaction":{"event_at":{"from":"2024-12-12T00:00:00.000+04:00","to":"2024-12-21T00:00:00.000+04:00"},"without_cash":true}}},"charset":"utf-8-sig"}'
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.post(url, json=payload) as response:
                logging.info(f"Response: {response.status} {response.reason} {url}")
                response.raise_for_status()
                return await response.json()

    async def get_payouts(self, operation_id, from_date, to_date):
        url = f"{self.base_url}/fleet/reports-builder/report/payouts?operation_id={operation_id}"

        payload = {
            "locale": "en",
            "payment_at_from": from_date,
            "payment_at_to": to_date,
            "statuses": ["created", "transmitted", "paid"],
            "park_tz_id": "Asia/Dubai",
            "park_clid": "400001783251"
        }

        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.post(url, json=payload) as response:
                logging.info(f"Response: {response.status} {response.reason} {url}")
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
                logging.info(f"Response: {response.status} {response.reason} {url}")
                response.raise_for_status()
                return await response.json()

    async def download_report(self, operation_id):
        url = f"{self.base_url}/fleet/reports-storage/v1/operations/download?operation_id={operation_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.get(url) as response:
                logging.info(f"Response: {response.status} {response.reason} {url}")
                response.raise_for_status()
                return await response.json()

    async def get_transactions_list(self):
        url = f"{self.base_url}/fleet/fleet-payouts-web/v1/transactions/list"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.get(url) as response:
                logging.info(f"Response: {response.status} {response.reason} {url}")
                response.raise_for_status()
                return await response.json()

    async def get_order_details(self, order_id, driver_profile_id, tz="Asia/Dubai"):
        encoded_tz = quote(tz)
        url = f"{self.base_url}/fleet/fleet-orders/v1/orders/item/card?id={order_id}&tz={encoded_tz}&driver_profile_id={driver_profile_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logging.info(f"{url}")
            async with session.get(url) as response:
                logging.info(f"Response: {response.status} {response.reason} {url}")
                response.raise_for_status()
                response_data = await response.json()

                order_number = None
                for section in response_data["sections"]:
                    for block in section.get("blocks", []):
                        if block["name"] == "Order number":
                            order_number = block["value"]["text"]
                            break
                    if order_number:
                        break

                print(f"Order number: {order_number}")

                transactions_info = response_data.get("transactions_info", {})

                flat_json = {}
                flat_json['order_number'] = order_number

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
