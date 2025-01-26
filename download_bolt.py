
from datetime import datetime, timedelta
import os

from utils.bolt_api_client import BoltAPIClient
from utils.config_utils import read_config
from utils.creds import read_api_keys
from utils.file_utils import save_file
from utils.format_utils import convert_timestamps_to_iso, flatten_json, flatten_list_json

config = read_config("config.yml")

if __name__ == "__main__":
    api_secrets = read_api_keys()
    client_id = api_secrets['client_id']
    client_secret = api_secrets['client_secret']
    company_id = "135422"

    bolt_client = BoltAPIClient(client_id, client_secret, company_id)

    # Define time range
    end_date = datetime.now() + timedelta(days=1)
    start_date = datetime.now() - timedelta(days=config['report_start_from'])
    end_ts = int(end_date.timestamp())
    start_ts = int(start_date.timestamp())

    # Print date range
    print(f"Generating report for the date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    orders = bolt_client.fleet_integration_v1_get_fleet_orders(offset=0, limit=5, start_ts=start_ts, end_ts=end_ts)
    orders_flat = flatten_list_json(orders['data']['orders'])
    orders_flat = convert_timestamps_to_iso(orders_flat)

    # Format filename with file-safe date range
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"{start_date_str}_to_{end_date_str}_{timestamp_str}_bolt_downloader.csv"

    # Save file to the configured output folder
    base_path = config['output_folder']
    full_path = os.path.join(base_path, filename)
    save_file(orders_flat, full_path, consistent_order=True)

    print(f"Report saved as: {full_path}")
    