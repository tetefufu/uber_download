
from datetime import datetime, timedelta
import logging

import requests

from utils.date_utils import get_latest_monday


class UberClient:
    def __init__(self, org_id, start_from, cookie_str):
        self.headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'x-csrf-token': 'x',
        }
        self.cookies = cookie_str
        self.url = 'https://supplier.uber.com/graphql'
        self.org_id = org_id
        self.start_from = start_from

    def get_dates(self):
        now = datetime.now()

        if self.start_from != 0:
            yesterday = now - timedelta(days=self.start_from)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = get_latest_monday()

        tomorrow = now + timedelta(days=0)
        end_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

        start_time_unix_millis = int(start_date.timestamp() * 1000)
        end_time_unix_millis = int(end_date.timestamp() * 1000)

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        return start_time_unix_millis, end_time_unix_millis, start_date_str, end_date_str


    def get_status(self):
        data = {
            'operationName': 'getLatestVsPaymentReport',
            'variables': {
                'orgUUID': self.org_id
            },
            'query': '''
                query getLatestVsPaymentReport($orgUUID: ID!) {
                  getLatestVsPaymentReport(orgUUID: $orgUUID) {
                    reportID
                    orgUUID
                    userUUID
                    paymentReportType
                    startDate
                    endDate
                    createdAt
                    completedAt
                    fileName
                    reportStatus
                    reportFailedReason
                    __typename
                  }
                }
            '''
        }

        response = requests.post(self.url, headers=self.headers, json=data, cookies=self.cookies)
        response.raise_for_status()
        response_data = response.json()
        logging.info(response_data)

        report_status = response_data['data']['getLatestVsPaymentReport']['reportStatus']
        filename = response_data['data']['getLatestVsPaymentReport']['fileName']

        return report_status, filename

    def download(self, report_id):
        data = {
            "operationName": "downloadVsPaymentReport",
            "variables": {
                "orgUUID": self.org_id,
                "reportID": report_id
            },
            "query": """
                query downloadVsPaymentReport($orgUUID: ID!, $reportID: ID!) {
                  downloadVsPaymentReport(orgUUID: $orgUUID, reportID: $reportID) {
                    signedURL
                    __typename
                  }
                }
            """
        }

        response = requests.post(self.url, headers=self.headers, json=data, cookies=self.cookies)
        response.raise_for_status()
        response_data = response.json()
        logging.info(response_data)

        signed_url = response_data['data']['downloadVsPaymentReport']['signedURL']

        return signed_url


    def generate(self, report_type):
        start_time_unix_millis, end_time_unix_millis, start_date_str, end_date_str = self.get_dates()
        data = {
            "operationName": "generateVsPaymentReport",
            "variables": {
                "orgUUID": self.org_id,
                "paymentReportType": report_type,
                "startDate": start_date_str,
                "endDate": end_date_str,
                "startTimeUnixMillis": str(start_time_unix_millis),
                "endTimeUnixMillis": str(end_time_unix_millis)
            },
            "query": """
                mutation generateVsPaymentReport($orgUUID: ID!, $paymentReportType: String!, $startDate: Date!, $endDate: Date!, $startTimeUnixMillis: String, $endTimeUnixMillis: String) {
                  generateVsPaymentReport(
                    orgUUID: $orgUUID
                    paymentReportType: $paymentReportType
                    startDate: $startDate
                    endDate: $endDate
                    startTimeUnixMillis: $startTimeUnixMillis
                    endTimeUnixMillis: $endTimeUnixMillis
                  ) {
                    reportID
                    __typename
                  }
                }
            """
        }

        response = requests.post(self.url, headers=self.headers, json=data, cookies=self.cookies)
        response.raise_for_status()
        response_data = response.json()
        logging.info(response_data)

        report_id = response_data['data']['generateVsPaymentReport']['reportID']

        return report_id