import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateAccount:
    @pytest.mark.usefixtures('user_request', 'api_manager')
    def test_create_account(self, api_manager: ApiManager, user_request: CreateUserRequest):
        created_account = api_manager.user_steps.create_account(user_request)
        check_created_account = api_manager.user_steps.get_account_by_id(created_account.id, user_request)

        assert check_created_account.id == created_account.id
        assert check_created_account.balance == created_account.balance
        assert check_created_account.balance == 0.0


