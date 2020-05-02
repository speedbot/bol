import json
import requests


class APIHandler:
    def __init__(self, client):
        self.client = client
        self.auth_token_url = 'https://login.bol.com/token?grant_type=client_credentials'
        self.shipment_list_url = 'https://api.bol.com/retailer/shipments/'

    def get_access_token(self):
        kwargs = {
            'client_id': self.client.client_id,
            'client_secret': self.client.client_secret,
            'grant_type': 'client_credentails',
        }
        response = requests.post(self.auth_token_url, kwargs)
        if response.status_code == 200:
            self.client.update_token_expiry()
            return json.loads(response.content.decode())['access_token']
        else:
            return None

    def get_all_shipments(self):
        header = 'Bearer {}'.format(self.get_access_token())
        response = requests.get(
            self.shipment_list_url,
            headers={'Authorization': header, 'Accept': 'application/vnd.retailer.v3+json'},
        )
        return json.loads(response.content.decode())