from http import HTTPStatus
import os

import requests

from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.requester import Requester


class TransferRequester(Requester):
    def __init__(self, request_spec=None, response_spec=None):
        request_spec = request_spec or {}
        base = (request_spec.get('base_url') or
                os.getenv('BASE_API_URL') or
                os.getenv('SERVER', 'http://localhost:4111/api').replace('/api', ''))
        base = base.rstrip('/')
        if not base.endswith('/api'):
            base = base + '/api'
        request_spec['base_url'] = base + '/v1'
        super().__init__(request_spec, response_spec)

    def post(self, transfer_request: TransferRequest) -> TransferResponse:
        url = f'{self.base_url}/accounts/transfer'
        response = requests.post(url=url, json=transfer_request.model_dump(), headers=self.headers)
        self.response_spec(response)
        if response.status_code == HTTPStatus.OK:
            return TransferResponse(**response.json())
