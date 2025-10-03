import pytest

from src.main.api.models.deposit_request import DepositRequest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.fixture
def deposit_setup(api_manager: ApiManager):
    user = CreateUserRequest(username=RandomData.get_username(), password=RandomData.get_password(), role="USER")
    api_manager.admin_steps.create_user(user)
    account = api_manager.user_steps.create_account(user)
    deposit_amount = RandomData.get_deposit_amount(1.0, 4999.0)
    deposit_request = DepositRequest(id=account.id, balance=deposit_amount)
    yield {"deposit_request": deposit_request, "user": user, "deposit_amount": deposit_amount}

