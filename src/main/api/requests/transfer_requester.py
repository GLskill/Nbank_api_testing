from http import HTTPStatus

import requests

from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.requester import Requester


class TransferRequester(Requester):
    def post(self, transfer_request: TransferRequest) -> TransferResponse:
        url = f'{self.base_url}/accounts/deposit'
        response = requests.post(url=url, json=transfer_request.model_dump(), headers=self.headers)
        self.request_spec(response)
        if response.status_code == HTTPStatus.OK:
            return TransferResponse(**response.json())
