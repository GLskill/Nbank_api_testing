from http import HTTPStatus

import requests

from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.requester import Requester


class TransferRequester(Requester):
    def post(self, transfer_request: TransferRequest) -> TransferResponse:
        url = f'{self.base_url}/accounts/transfer'

        print(f"\n=== TRANSFER REQUEST DEBUG ===")
        print(f"URL: {url}")
        print(f"Headers: {self.headers}")
        print(f"Body: {transfer_request.model_dump()}")

        response = requests.post(url=url, json=transfer_request.model_dump(), headers=self.headers)

        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        print(f"=== END DEBUG ===\n")

        self.response_spec(response)
        if response.status_code == HTTPStatus.OK:
            return TransferResponse(**response.json())