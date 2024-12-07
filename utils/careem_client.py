import asyncio
import aiohttp

from datetime import datetime, timedelta
import logging

import requests

from utils.date_utils import get_latest_monday
from urllib.parse import quote


class CareemClient:
    def __init__(self, org_id, start_from, bearer_token):
        self.headers = {
            "Authorization": "Bearer " + bearer_token,
            "Accept": "application/json, text/plain, */*",
        }
        self.bearer_token = bearer_token
        self.url = 'https://supplier.careem.com/api'
        self.captain_url = 'https://captain.careem.com/api'
        self.org_id = org_id
        self.start_from = start_from

    def get_dates(self):
        now = datetime.now()

        if self.start_from != 0:
            yesterday = now - timedelta(days=self.start_from)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = get_latest_monday()

        tomorrow = now + timedelta(days=1)
        end_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

        start_time_unix_millis = int(start_date.timestamp() * 1000)
        end_time_unix_millis = int(end_date.timestamp() * 1000)

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        return start_time_unix_millis, end_time_unix_millis, start_date_str, end_date_str


    async def get_trip_details(self, trip_id, captain_id):
        url = f"{self.captain_url}/trip-receipt/{trip_id}/en"
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "authcaptainid": str(captain_id),
            "authtoken": f"Bearer {self.bearer_token}",
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                response_data = await response.json()
                logging.info(response_data)

                flat_json = {}
                for section in response_data.get("data", {}).get("sections", []):
                    for line in section.get("lines", []):
                        left = line.get("left")
                        right = line.get("right")
                        
                        if left and right:
                            flat_json[left] = right

                return flat_json


    async def get_trips(self, captain_id, cycle_number = 0):
        url = f"{self.captain_url}/transaction/{captain_id}?cycleNumber=0&viewParams=%7B%22cycleIdx%22:%200%7D&viewType=cycle"
        

        # Encode the relevant part of the URL (the `viewParams` value)
        encoded_view_params = quote(f'{{"cycleIdx": {cycle_number}}}', safe=":")
        url = f"{self.captain_url}/transaction/{captain_id}?cycleNumber={cycle_number}&viewParams={encoded_view_params}&viewType=cycle"
        
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "authcaptainid": str(captain_id),
            "authtoken": f"Bearer {self.bearer_token}",
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                response_data = await response.json()
                logging.info(response_data)

                transactions = response_data["verifiedEarningPromise"]["captainTransactions"]

                result = [
                    {
                        "transactionId": transaction["transactionId"],
                        "captainName": response_data["verifiedEarningPromise"]["captainName"],
                        "captainId": response_data["verifiedEarningPromise"]["captainId"],
                        "countryName": response_data["verifiedEarningPromise"]["countryName"],
                        "uuid": transaction["uuid"]
                    }
                    for transaction in transactions
                ]

                return result


    async def get_drivers(self):
        start_time_unix_millis, end_time_unix_millis, start_date_str, end_date_str = self.get_dates()
        logging.info(f"Gettings driver")

        url = self.url + "/limo/portal/captain/acceptance/477236"
        params = {
            "startTime": str(start_time_unix_millis),
            "endTime": str(end_time_unix_millis)
        }

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                response_data = await response.json()
                logging.info(response_data)

                captain_ids = [entry['captainId'] for entry in response_data]

                return captain_ids
