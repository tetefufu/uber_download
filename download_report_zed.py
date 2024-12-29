import logging
import os
from datetime import datetime

import requests

from utils.config_utils import read_config
from utils.creds import extract_access_token
from utils.date_utils import generate_dates_rolling_zed_format
from utils.zed_client import ZedClient
from utils.log_utils import *

config = read_config("config.yml")
access_token = extract_access_token()
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

    start_date_str = start_date.split(" ")[0]
    end_date_str = end_date.split(" ")[0]
    filename = os.path.join(config.get("output_folder", "./reports"), f"zed_report_{start_date_str}_to_{end_date_str}.csv")

    logging.info(f"Downloading report to {filename}")
    download_and_save_file(filename, document_url)


if __name__ == "__main__":
    start_date, end_date = generate_dates_rolling_zed_format(config.get("report_start_from", 30))
    output_folder = config.get("output_folder", "./reports")
    filename = os.path.join(output_folder, "zed_report.csv")

    generate_and_download_report(start_date, end_date, filename)
