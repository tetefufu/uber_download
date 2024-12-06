import logging
import os

from utils.careem_client import CareemClient
from utils.config_utils import read_config
from utils.creds import extract_bearer_token

from utils.log_utils import *

bearer_token = extract_bearer_token()
bearer_token = 'eyJraWQiOiI3MmM5NTU0OS0zZjI4LTRiNTEtOWYyZi02OTdiNTI0NTFkMzUiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI2NTk3MzYwNSIsImF1ZCI6ImNvbS5jYXJlZW0uaW50ZXJuYWwiLCJsaW1vX3BvcnRhbFwvc291cmNlX2FwcCI6IkxJTU9fUE9SVEFMIiwiYWNjZXNzX3R5cGUiOiJDVVNUT01FUiIsInVzZXJfaWQiOjY1OTczNjA1LCJhenAiOiIyNjIyZDRhZi1lZGE0LTQyZWMtYTk1NC05NDdlMDk3NGY4MjEuc3VwcGxpZXIuY2FyZWVtLmNvbSIsImtpbmQiOiJDVVNUT01FUiIsInNjb3BlIjoib3BlbmlkIGVkZ2VfY2FwdGFpbiBwcm9maWxlIiwiaXNzIjoiaHR0cHM6XC9cL2lkZW50aXR5LmNhcmVlbS5jb21cLyIsImV4cCI6MTczMzUwMDYyNiwiaWF0IjoxNzMzNDE0MjI2LCJqdGkiOiJjYTAzMTgzNy00MzJkLTQyNDktYThhYS1iZDkzMGFjYTExZmQifQ.ByRk3u7LQ5XWLkeW23iKlxoiTLUOpJsS_xv5pLePe0XV68Jt089EaWsx-YbfxbQGVR8lGCXd72d42WxzU8nnhaDPAxogPsayI2K2hnTtGUMRyk30iTe41GOEdxhiNNbjK7ZMucS1K-cwXF417psqDpaA1HEBTBsnIP_e0mc6O16doOCklGkxc-bdENteUcaERv6EFvaifkWk9neqWfDNunh7-D04jrwmjotWMN4GtQEsE8lcUnvrDwWq7JgPZeL2O4Cmt8MYW3Pz7Xv5Byp5CeBYO2cjq0HGCwNoNk9e8MA_AW_47xGH_dhHeEHhJCRfTf9lOsVdG9kyh6zjE5ElMg'
config = read_config("config.yml")
client = CareemClient(org_id=1, start_from=config['report_start_from'], bearer_token=bearer_token)


def get_captain_ids():
    captain_ids = client.get_drivers()
    return captain_ids


def get_trips(drivers):
    # trips = client.get_trips(drivers[0])
    for driver in drivers:
        trips = client.get_trips(driver)
        for trip in trips:
            trip_details = client.get_trip_details(trip['transactionId'], driver)


def save_file(url, filename):
    pass


if __name__ == "__main__":
    # captain_ids = get_captain_ids()
    captain_ids = [3226722]
    trips = get_trips(captain_ids)

    # filename = "test.csv"
    # base_path = config['output_folder']
    # full_path = os.path.join(base_path, filename) + ".csv"
    # save_file(trips, full_path)
