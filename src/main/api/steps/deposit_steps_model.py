from src.main.api.models.deposit_request import DepositRequest
from src.main.api.requests.deposit_reqester import DepositRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


class DepositSteps:
    @staticmethod
    def make_deposit(account_id: str, amount: float, username: str, password: str):
        deposit_request = DepositRequest(id=account_id, balance=amount)
        return DepositRequester(
            RequestSpecs.user_auth_spec(username, password),
            ResponseSpecs.request_return_ok()
        ).post(deposit_request)
