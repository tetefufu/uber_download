import logging
import os
import re
import time
from datetime import datetime, timedelta

import requests
import yaml

def extract_cookie_value():
    # Open the curl.txt file from the same directory as the script
    with open('curl.txt', 'r') as file:
        curl_content = file.read()

    # Regular expression pattern to match the cookie value after 'cookie:'
    pattern = r"-H\s+'cookie:\s*([^']+)'"

    # Search for the pattern in the content of the file
    match = re.search(pattern, curl_content)

    if match:
        # Extract the cookie value from the matched group
        cookie_value = match.group(1).strip()
        return cookie_value
    else:
        return None  # Return None if no match found

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)  # Log all messages to the file
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)  # Log all messages to the console
log_format = '%(asctime)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# from Scripts.uber_client import UberClient, download_and_save_file

cookie_str = extract_cookie_value()

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)  # safely loads the yaml file
    return config


config = read_config("config.yml")


def get_latest_monday():
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    latest_monday = datetime(monday.year, monday.month, monday.day)
    return latest_monday


class UberClient:
    def __init__(self, org_id, start_from):
        self.headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'cookie': cookie_str,
            'x-csrf-token': 'x',
        }
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

        response = requests.post(self.url, headers=self.headers, json=data)
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

        response = requests.post(self.url, headers=self.headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        logging.info(response_data)

        signed_url = response_data['data']['downloadVsPaymentReport']['signedURL']

        return signed_url


    def generate(self):
        start_time_unix_millis, end_time_unix_millis, start_date_str, end_date_str = self.get_dates()
        data = {
            "operationName": "generateVsPaymentReport",
            "variables": {
                "orgUUID": self.org_id,
                "paymentReportType": "REPORT_TYPE_PAYMENTS_ORDER",
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

        response = requests.post(self.url, headers=self.headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        logging.info(response_data)

        report_id = response_data['data']['generateVsPaymentReport']['reportID']

        return report_id


def download_and_save_file(filename, url):
    response = requests.get(url)

    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)

    logging.info(f"File saved as {filename}")

client = UberClient(org_id=config['org_id'], start_from=config['report_start_from'])

def generate_report():
    return client.generate()




def wait_for_report_completion():
    status, filename = client.get_status()
    while status == 'REPORT_STATUS_IN_PROGRESS':
        logging.info(f"Report is still in progress... Current status: {status}")
        time.sleep(5)
        status, filename = client.get_status()

    logging.info(status) # 'REPORT_STATUS_COMPLETED'
    return status, filename


def get_download_url(report_id):
    return client.download(report_id)


def save_file(url, filename):
    logging.info(f"downloading {filename} from {url}")
    download_and_save_file(filename=filename, url=url)


if __name__ == "__main__":
    report_id = generate_report()
    status, filename = wait_for_report_completion()
    download_url = get_download_url(report_id)

    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename) + ".csv"
    save_file(download_url, full_path)
