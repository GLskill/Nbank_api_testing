import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.admin_steps_model import AdminSteps
from src.main.api.models.deposit_steps_model import DepositSteps
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.user_steps_model import UserSteps
from src.main.api.requests.admin_user_requester import AdminUserRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.transfer_requester import TransferRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestTransfer:

    def test_transfer_successful(self):
        username1 = RandomData.get_username()
        password1 = RandomData.get_password()
        role1 = 'USER'
        username2 = RandomData.get_username()
        password2 = RandomData.get_password()
        role2 = 'USER'
        try:
            create_user1_response = AdminSteps.create_user(username1, password1, role1)
            create_user2_response = AdminSteps.create_user(username2, password2, role2)

            create_account1_response = UserSteps.create_account(username1, password1)
            create_account2_response = UserSteps.create_account(username2, password2)

            deposit_amount = RandomData.get_deposit_amount(100.0, 5000.0)
            DepositSteps.make_deposit(create_account1_response.id, deposit_amount, username1, password1)

            transfer_amount = deposit_amount * 0.5
            transfer_request = TransferRequest(
                senderAccountId=create_account1_response.id,
                receiverAccountId=create_account2_response.id,
                amount=transfer_amount
            )

            transfer_response = TransferRequester(
                RequestSpecs.user_auth_spec(create_user1_response.username1, create_user1_response.password2),
                ResponseSpecs.request_return_ok()
            ).post(transfer_request)

            assert transfer_response.message == "Transfer successful"
            assert transfer_response.senderAccountId == create_account1_response.id
            assert transfer_response.receiverAccountId == create_account2_response.id
            assert transfer_response.amount == transfer_amount

            get_account1_after_transfer = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user1_response.username1, create_user1_response.password1),
                ResponseSpecs.request_return_ok()
            ).get()

            assert get_account1_after_transfer.balance == deposit_amount - transfer_amount
            assert any(
                transaction.type == "TRANSFER_OUT" and transaction.amount == transfer_amount
                for transaction in get_account1_after_transfer.transactions
            )

            get_account2_after_transfer = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user2_response.username2, create_user2_response.password2),
                ResponseSpecs.request_return_ok()
            ).get()

            assert get_account2_after_transfer.balance == transfer_amount
            assert any(
                transaction.type == "TRANSFER_IN" and transaction.amount == transfer_amount
                for transaction in get_account2_after_transfer.transactions
            )

        finally:
            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_deleted()
            ).delete(create_account1_response.id)
            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_deleted()
            ).delete(create_account2_response.id)

