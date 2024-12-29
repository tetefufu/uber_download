import logging
import os
from datetime import datetime

import requests

from utils.config_utils import read_config
from utils.zed_client import ZedClient
from utils.log_utils import *

config = read_config("config.yml")
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjczZTdiN2MzNDYxN2E2YzI3NjIwYTEiLCJ1c2VyVHlwZSI6MywiaWF0IjoxNzM1NDUwMTYzLCJleHAiOjE3MzU1MTAxNjN9.3-o6MCe2Kt_nOHRha1DUBCkJKv-ukPQvYhrPz5THZAQ"
client = ZedClient(access_token=access_token)


def download_and_save_file(filename, url):
    response = requests.get(url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)

    logging.info(f"File saved as {filename}")


def generate_and_download_report(start_date, end_date, filename):
    logging.info(f"Generating report from {start_date} to {end_date}")
    document_url = client.generate_report(start_date, end_date)
    logging.info(f"Downloading report to {filename}")
    download_and_save_file(filename, document_url)


if __name__ == "__main__":
    start_date = config.get("report_start_date", "2024-12-01 00:00:00")
    end_date = config.get("report_end_date", "2024-12-19 23:59:59")
    output_folder = config.get("output_folder", "./reports")
    filename = os.path.join(output_folder, "zed_report.csv")

    generate_and_download_report(start_date, end_date, filename)
