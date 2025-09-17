import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models import create_user_request
from src.main.api.models.admin_steps_model import AdminSteps
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.user_steps_model import UserSteps
from src.main.api.requests.admin_user_requester import AdminUserRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.deposit_reqester import DepositRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.requests.deposit_reqester import DepositRequester


@pytest.mark.api
class TestAccountDeposit:
    @pytest.mark.parametrize(
        "username, password, role",
        [(RandomData.get_username(), RandomData.get_password(), 'USER'), ]
    )
    def test_successful_deposit(self, username: str, password: str, role: str):
        create_user_response = AdminSteps.create_user(username, password, role)
        create_account_response = UserSteps.create_account(username, password)

        deposit_amount = RandomData.get_deposit_amount(1.0, 100000.0)
        deposit_request = DepositRequest(id=create_account_response.id, balance=deposit_amount)
        deposit_response = DepositRequester(
            RequestSpecs.user_auth_spec(username, password),
            ResponseSpecs.request_return_ok()
        ).post(deposit_request)

        assert deposit_response.balance == deposit_amount
        assert any(
            transaction.type == "DEPOSIT" and transaction.amount == deposit_amount
            for transaction in deposit_response.transactions
        )

        get_account_response = CreateAccountRequester(
            RequestSpecs.user_auth_spec(username, password),
            ResponseSpecs.request_return_ok()
        ).get()

        assert get_account_response.balance == deposit_amount
        assert any(
            transaction.type == "DEPOSIT" and transaction.amount == deposit_amount
            for transaction in get_account_response.transactions
        )
