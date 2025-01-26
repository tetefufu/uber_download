import requests
from datetime import datetime, timedelta

class BoltAPIClient:
    def __init__(self, client_id, client_secret, company_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.company_id = company_id
        self.token_url = "https://oidc.bolt.eu/token"
        self.base_url = "https://node.bolt.eu/fleet-integration-gateway"
        self.access_token = None
        self.token_expiry = None

    def _get_new_token(self):
        """Fetch a new access token from the Bolt API."""
        response = requests.post(
            self.token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": "fleet-integration:api",
            },
        )
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"] - 60)
        else:
            raise Exception(f"Failed to fetch token: {response.status_code} - {response.text}")

    def _ensure_valid_token(self):
        """Ensure the access token is valid, refreshing it if necessary."""
        if not self.access_token or datetime.now() >= self.token_expiry:
            self._get_new_token()

    def _request(self, method, endpoint, params=None, json=None):
        """Make an authenticated request to the Bolt API."""
        self._ensure_valid_token()
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.request(method, url, headers=headers, params=params, json=json)
        if response.status_code >= 200 and response.status_code < 300 and response.json()['code'] == 0:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

    def fleet_integration_v1_get_fleet_orders(self, offset=0, limit=10, start_ts=None, end_ts=None):
        """Fetch fleet orders using the fleetIntegrationV1GetFleetOrders endpoint."""
        endpoint = "fleetIntegration/v1/getFleetOrders"
        json_data = {
            "offset": offset,
            "limit": limit,
            "company_ids": [self.company_id],
            "start_ts": start_ts if start_ts else 0,
            "end_ts": end_ts if end_ts else 0,
        }
        return self._request("POST", endpoint, json=json_data)