from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.deposit_response import DepositResponse
from src.main.api.requests.deposit_reqester import DepositRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class DepositSteps(BaseSteps):
    def make_deposit(self, account_id: str, amount: float, username: str, password: str) -> DepositResponse:
        deposit_request = DepositRequest(id=account_id, balance=amount)
        deposit_response = DepositRequester(
            RequestSpecs.user_auth_spec(username, password),
            ResponseSpecs.request_return_ok()
        ).post(deposit_request)
        self.created_objects.append(deposit_response)
        return deposit_response
