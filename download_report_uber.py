import logging
import os
import time

import requests

from utils.config_utils import read_config
from utils.creds import extract_cookie_value
from utils.uber_client import UberClient

from utils.log_utils import *

cookie_str = extract_cookie_value()
config = read_config("config.yml")
client = UberClient(org_id=config['org_id'], start_from=config['report_start_from'], cookie_str=cookie_str)


def download_and_save_file(filename, url):
    response = requests.get(url)

    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)

    logging.info(f"File saved as {filename}")


def generate_report(report_type):
    return client.generate(report_type)


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


def generate_report_type(report_type):
    report_id = generate_report(report_type)
    status, filename = wait_for_report_completion()
    download_url = get_download_url(report_id)

    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename) + ".csv"
    save_file(download_url, full_path)


if __name__ == "__main__":
    if 'reports' in config:
        reports = config['reports']
        for report in reports:
            generate_report_type(report)
    else:
        generate_report_type("REPORT_TYPE_PAYMENTS_ORDER")
        