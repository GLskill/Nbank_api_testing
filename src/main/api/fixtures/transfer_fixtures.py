import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transfer_request import TransferRequest


@pytest.fixture
def transfer_setup(api_manager: ApiManager, deposit_setup):
    api_manager.user_steps.deposit_to_account(
        deposit_setup["user"],
        deposit_setup["deposit_request"]
    )
    user2 = CreateUserRequest(username=RandomData.get_username(), password=RandomData.get_password(), role="USER")
    api_manager.admin_steps.create_user(user2)
    account2 = api_manager.user_steps.create_account(user2)

    transfer_request = TransferRequest(
        senderAccountId=deposit_setup["deposit_request"].id,
        receiverAccountId=account2.id,
        amount=deposit_setup["deposit_amount"] * 0.5
    )

    yield {"transfer_request": transfer_request, "user1": deposit_setup["user"], "user2": user2}

