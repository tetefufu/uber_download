import csv
from datetime import datetime
import logging
import os

from utils.careem_client import CareemClient
from utils.config_utils import read_config
from utils.creds import extract_bearer_token

from utils.log_utils import *

bearer_token = extract_bearer_token()
bearer_token = 'eyJraWQiOiI3MmM5NTU0OS0zZjI4LTRiNTEtOWYyZi02OTdiNTI0NTFkMzUiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI2NTk3MzYwNSIsImF1ZCI6ImNvbS5jYXJlZW0uaW50ZXJuYWwiLCJsaW1vX3BvcnRhbFwvc291cmNlX2FwcCI6IkxJTU9fUE9SVEFMIiwiYWNjZXNzX3R5cGUiOiJDVVNUT01FUiIsInVzZXJfaWQiOjY1OTczNjA1LCJhenAiOiIyNjIyZDRhZi1lZGE0LTQyZWMtYTk1NC05NDdlMDk3NGY4MjEuc3VwcGxpZXIuY2FyZWVtLmNvbSIsImtpbmQiOiJDVVNUT01FUiIsInNjb3BlIjoib3BlbmlkIGVkZ2VfY2FwdGFpbiBwcm9maWxlIiwiaXNzIjoiaHR0cHM6XC9cL2lkZW50aXR5LmNhcmVlbS5jb21cLyIsImV4cCI6MTczMzUwMDYyNiwiaWF0IjoxNzMzNDE0MjI2LCJqdGkiOiJjYTAzMTgzNy00MzJkLTQyNDktYThhYS1iZDkzMGFjYTExZmQifQ.ByRk3u7LQ5XWLkeW23iKlxoiTLUOpJsS_xv5pLePe0XV68Jt089EaWsx-YbfxbQGVR8lGCXd72d42WxzU8nnhaDPAxogPsayI2K2hnTtGUMRyk30iTe41GOEdxhiNNbjK7ZMucS1K-cwXF417psqDpaA1HEBTBsnIP_e0mc6O16doOCklGkxc-bdENteUcaERv6EFvaifkWk9neqWfDNunh7-D04jrwmjotWMN4GtQEsE8lcUnvrDwWq7JgPZeL2O4Cmt8MYW3Pz7Xv5Byp5CeBYO2cjq0HGCwNoNk9e8MA_AW_47xGH_dhHeEHhJCRfTf9lOsVdG9kyh6zjE5ElMg'
bearer_token = 'eyJraWQiOiI5ZWRhYzI2MC1iZGRiLTRiNjUtOTAxMi1mMmQ3MGUyNDJiYzYiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI2NTk3MzYwNSIsImF1ZCI6ImNvbS5jYXJlZW0uaW50ZXJuYWwiLCJsaW1vX3BvcnRhbFwvc291cmNlX2FwcCI6IkxJTU9fUE9SVEFMIiwiYWNjZXNzX3R5cGUiOiJDVVNUT01FUiIsInVzZXJfaWQiOjY1OTczNjA1LCJhenAiOiIyNjIyZDRhZi1lZGE0LTQyZWMtYTk1NC05NDdlMDk3NGY4MjEuc3VwcGxpZXIuY2FyZWVtLmNvbSIsImtpbmQiOiJDVVNUT01FUiIsInNjb3BlIjoib3BlbmlkIGVkZ2VfY2FwdGFpbiBwcm9maWxlIiwiaXNzIjoiaHR0cHM6XC9cL2lkZW50aXR5LmNhcmVlbS5jb21cLyIsImV4cCI6MTczMzU4NzI2MiwiaWF0IjoxNzMzNTAwODYyLCJqdGkiOiJjNGUzYmYxYi1mNmE5LTRkZWMtOTAxZS04YWY2ZjM3OTllMmIifQ.AxgVaOriZcVc2_Uron1v58qgI-3lQJdj6vFx6bl4v_ZZZROB4QIH_NFAd_koruafsomOWklmPJIu2LKCBuPrgiGEKNPCLtDX3QPtUq5ED2m3o6KVnYWhkpGYnvOnP9Kdw8JT-aFmRGzkQGkTG8FkDVHhJI9OvX3hrDiMu96gp4w6xv5KSSNBAH1HcGJuroEjfgeCtWiT6kRRLRfK5WzOtF8EfXsIY0IvBb-aMTz4uhfCvWql_Tht-J0pLdji0z-k668hZi0-QR_oQ0hkAl80O159zWGUtMgNJ8Don7HB44kp05Za01ctkHgXcwZ9cVhU6eDm6cSKqIuhfa6xau2Zpg'
config = read_config("config.yml")
client = CareemClient(org_id=1, start_from=config['report_start_from'], bearer_token=bearer_token)


def get_captain_ids():
    captain_ids = client.get_drivers()
    return captain_ids


def get_trips(drivers):
    extended_trips = []
    for driver in drivers:
        trips = client.get_trips(driver)
        for trip in trips:
            trip_details = client.get_trip_details(trip['transactionId'], driver)
            extended_trip = {**trip, **trip_details}
            extended_trips.append(extended_trip)
    return extended_trips


def save_file(list_of_dicts, filepath):
    logging.info(f"saving {filepath}")
    if not list_of_dicts:
        raise ValueError("The list of dictionaries is empty.")

    header = set()
    for dictionary in list_of_dicts:
        header.update(dictionary.keys())
    header = list(header)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(list_of_dicts)
    logging.info(f"saved to file {filepath}")


if __name__ == "__main__":
    captain_ids = get_captain_ids()
    trips = get_trips(captain_ids)

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M')}_careem_downloader.csv"
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename) + ".csv"
    save_file(trips, full_path)
