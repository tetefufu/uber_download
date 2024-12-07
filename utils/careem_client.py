import aiohttp

from datetime import datetime, timedelta
import logging

from utils.date_utils import get_latest_monday
from urllib.parse import quote
from flatten_json import flatten


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
                flat_json['tripDate'] = response_data.get('tripDate', None)
                flat_json['earnings'] = response_data.get('earnings', None)
                flat_json['carInfo'] = response_data.get('carInfo', None)
                flat_json['meta'] = response_data.get('meta', None)
                for section in response_data.get("data", {}).get("sections", []):
                    for line in section.get("lines", []):
                        left = line.get("left")
                        right = line.get("right")
                        
                        if left and right:
                            flat_json[left] = right

                return flat_json


    async def get_trips(self, captain_id, cycle_number = 0):
        logging.info(f'get_trips {captain_id=} {cycle_number=}')
        encoded_view_params = quote(f'{{"cycleIdx": {cycle_number}}}', safe=":")
        url = f"{self.captain_url}/transaction/{captain_id}?cycleNumber={cycle_number}&viewParams={encoded_view_params}&viewType=cycle"
        
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "authcaptainid": str(captain_id),
            "authtoken": f"Bearer {self.bearer_token}",
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                def filter_out_lists_recursive(json_data):
                    """
                    Recursively filter out all list fields from the JSON data.
                    
                    Args:
                    - json_data (dict): The input JSON object.
                    
                    Returns:
                    - dict: The filtered JSON with lists removed.
                    """
                    if isinstance(json_data, dict):
                        # Iterate through dictionary items and recursively filter out lists
                        return {key: filter_out_lists_recursive(value) for key, value in json_data.items() if not isinstance(value, list)}
                    elif isinstance(json_data, list):
                        # If the value is a list, return an empty list to exclude it
                        return []
                    else:
                        # For non-dictionary and non-list values, just return the value
                        return json_data


                response.raise_for_status()
                response_data = await response.json()
                logging.info(response_data)

                filtered_data = filter_out_lists_recursive(response_data)

                # Flatten the filtered JSON
                flat_json = flatten(filtered_data)
                flat_json["transactionId"] = "None"

                # Initialize the result with captain info
                result = flat_json

                # Get transactions, or return a list with one default item if not present
                transactions = response_data.get("verifiedEarningPromise", {}).get("captainTransactions", [])

                if transactions:
                    result = []
                    for transaction in transactions:
                        transaction_no_lists = filter_out_lists_recursive(transaction)
                        result.append({**flat_json, **transaction_no_lists})
                    return result

                return [flat_json]


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
