import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.deposit_response import DepositResponse


@pytest.mark.api
class TestAccountDeposit:
    @pytest.mark.usefixtures('user_request', 'api_manager')
    @pytest.mark.parametrize('deposit_amount', [RandomData.get_deposit_amount(1.0, 4999.0)])
    def test_successful_deposit(self, api_manager: ApiManager, user_request: CreateUserRequest, deposit_amount):
        create_account_response = api_manager.user_steps.create_account(user_request)
        deposit_request = DepositRequest(id=create_account_response.id, balance=deposit_amount)
        deposit_response = api_manager.user_steps.deposit_to_account(user_request, deposit_request)

        assert deposit_response.balance == deposit_amount

