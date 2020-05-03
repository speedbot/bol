import json

import requests
from ratelimit import limits

from .constants import BOL_LOGIN_URL, BOL_SHIPMENT_URL


class APIHandler:
    def __init__(self, client):
        self.client = client

    def get_access_token(self):
        if not self.client.is_expired():
            return self.client.auth_token
        kwargs = {
            'client_id': self.client.client_id,
            'client_secret': self.client.client_secret,
            'grant_type': 'client_credentails',
        }
        response = requests.post(BOL_LOGIN_URL, kwargs)
        if response.status_code == 200:
            auth_token = json.loads(response.content.decode())['access_token']
            self.client.update_auth_token(auth_token)
            return auth_token
        else:
            return None

    def get_headers(self):
        header = 'Bearer {}'.format(self.get_access_token())
        return {'Authorization': header, 'Accept': 'application/vnd.retailer.v3+json'}

    @limits(calls=7, period=60)
    def get_shipment_data(self, params=None):
        response = requests.get(
            BOL_SHIPMENT_URL,
            headers=self.get_headers(),
            params=params,
        )
        if response.status_code == 200:
            return json.loads(response.content.decode())
        else:
            return None

    @limits(calls=14, period=60)
    def get_shipment(self, shipmentId):
        response = requests.get(
            '{}{}/'.format(BOL_SHIPMENT_URL, shipmentId),
            headers=self.get_headers(),
        )
        if response.status_code == 200:
            return json.loads(response.content.decode())
        else:
            return None
