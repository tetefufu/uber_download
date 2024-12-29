# zed_client.py
import requests
import logging

class ZedClient:
    def __init__(self, access_token):
        self.url = "https://api.supplier.gozed.ae/api/supplier/report/supplierPayout"
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'accesstoken': access_token
        }

    def generate_report(self, start_date, end_date):
        data = {
            "startDate": start_date,
            "endDate": end_date
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        response.raise_for_status()
        response_data = response.json()

        if "data" in response_data and "documentUrl" in response_data["data"]:
            document_url = response_data["data"]["documentUrl"]
            logging.info(f"Report generated: {document_url}")
            return document_url
        else:
            logging.error("Failed to generate report: Unexpected response format")
            raise ValueError("Failed to generate report")
