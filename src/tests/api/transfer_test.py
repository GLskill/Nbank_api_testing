import pytest

from src.main.api.classes.api_manager import ApiManager


@pytest.mark.api
class TestTransfer:
    @pytest.mark.usefixtures("api_manager", "transfer_setup")
    def test_transfer_successful(self, api_manager: ApiManager, transfer_setup):
        response = api_manager.user_steps.transfer_money(transfer_setup["transfer_request"], transfer_setup["user1"])

        assert response.message == "Transfer successful"
        assert response.senderAccountId == transfer_setup["transfer_request"].senderAccountId
        assert response.receiverAccountId == transfer_setup["transfer_request"].receiverAccountId
        assert response.amount == transfer_setup["transfer_request"].amount
