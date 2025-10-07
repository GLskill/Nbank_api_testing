import pytest

from src.main.api.classes.api_manager import ApiManager


@pytest.mark.api
class TestAccountDeposit:
    @pytest.mark.usefixtures("api_manager", "deposit_setup")
    def test_successful_deposit(self, api_manager: ApiManager, deposit_setup):
        response = api_manager.user_steps.deposit_to_account(deposit_setup["user"], deposit_setup["deposit_request"])

        assert response.balance == deposit_setup["deposit_amount"]
        assert response.balance > 0
        assert response.id == deposit_setup["deposit_request"].id

        account_after_deposit = api_manager.user_steps.get_account_by_id(response.id, deposit_setup["user"])

        assert response.balance == deposit_setup["deposit_amount"]
        assert response.balance > 0
        assert response.id == deposit_setup["deposit_request"].id
