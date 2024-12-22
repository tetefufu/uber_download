import aiohttp
import logging
from datetime import datetime
from urllib.parse import quote

class YangoClient:
    def __init__(self, bearer_token):
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Accept": "application/json, text/plain, */*",
        }
        self.base_url = "https://fleet.yango.com/api"
        self.bearer_token = bearer_token

    async def get_transactions(self, operation_id):
        """
        Fetches transactions report asynchronously.

        Args:
        - operation_id (str): The operation ID for the transaction report.

        Returns:
        - dict: JSON response containing transaction details.
        """
        url = f"{self.base_url}/v1/reports/transactions/park/download-async?operation_id={operation_id}"
        logging.info(f"Fetching transactions with operation_id={operation_id}")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_payouts_list(self):
        """
        Fetches the list of payouts.

        Returns:
        - dict: JSON response containing payout details.
        """
        url = f"{self.base_url}/fleet/fleet-payouts-web/v2/payouts/list"
        logging.info("Fetching payouts list")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_report_status(self, operation_id):
        """
        Checks the status of a report operation.

        Args:
        - operation_id (str): The operation ID for the report.

        Returns:
        - dict: JSON response containing the report status.
        """
        url = f"{self.base_url}/fleet/reports-storage/v1/operations/status?operation_id={operation_id}"
        logging.info(f"Checking report status for operation_id={operation_id}")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def download_report(self, operation_id):
        """
        Downloads a report based on the operation ID.

        Args:
        - operation_id (str): The operation ID for the report.

        Returns:
        - dict: JSON response containing the download link and file name.
        """
        url = f"{self.base_url}/fleet/reports-storage/v1/operations/download?operation_id={operation_id}"
        logging.info(f"Downloading report for operation_id={operation_id}")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_transactions_list(self):
        """
        Fetches a list of transactions.

        Returns:
        - dict: JSON response containing transaction details.
        """
        url = f"{self.base_url}/fleet/fleet-payouts-web/v1/transactions/list"
        logging.info("Fetching transactions list")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_order_details(self, order_id, driver_profile_id, tz="Asia/Dubai"):
        """
        Fetches detailed information for a specific order.

        Args:
        - order_id (str): The order ID.
        - driver_profile_id (str): The driver profile ID.
        - tz (str): Timezone for the query (default: Asia/Dubai).

        Returns:
        - dict: JSON response containing order details.
        """
        encoded_tz = quote(tz)
        url = f"{self.base_url}/fleet/fleet-orders/v1/orders/item/card?id={order_id}&tz={encoded_tz}&driver_profile_id={driver_profile_id}"
        logging.info(f"Fetching order details for order_id={order_id}, driver_profile_id={driver_profile_id}")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
