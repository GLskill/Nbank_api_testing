import requests
from http import HTTPStatus
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.deposit_response import DepositResponse
from src.main.api.requests.requester import Requester


class DepositRequester(Requester):
    def post(self, deposit_request: DepositRequest) -> DepositResponse:
        url = f'{self.base_url}/accounts/deposit'
        response = requests.post(url=url, json=deposit_request.model_dump(), headers=self.headers)
        self.request_spec(response)
        if response.status_code == HTTPStatus.OK:
            return DepositResponse(**response.json())

