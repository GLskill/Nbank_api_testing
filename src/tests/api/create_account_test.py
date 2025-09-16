import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.requests.admin_user_requester import AdminUserRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.deposit_reqester import DepositRequester
from src.main.api.requests.transfer_requester import TransferRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.models.deposit_request import DepositRequest


@pytest.mark.api
class TestCreateAccount:
    @pytest.mark.parametrize(
        "username, password, role",
        [(RandomData.get_username(), RandomData.get_password(), 'USER'),]
    )
    def test_create_account(self, username: str, password: str, role: str):
        create_user_request = CreateUserRequest(username=username, password=password, role=role)

        create_user_response = AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_created()
        ).post(create_user_request)

        assert create_user_response.username == create_user_request.username
        assert create_user_response.role == create_user_request.role

        try:
            create_account1_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.entity_was_created()
            ).post()

            get_account1_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.request_return_ok()
            ).get(create_account1_response.id)

            assert create_account1_response.balance == 0.0
            assert not create_account1_response.transactions

            create_account2_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.entity_was_created()
            ).post()

            get_account2_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.request_return_ok()
            ).get(create_account2_response.id)

            assert create_account2_response.balance == 0.0
            assert not create_account2_response.transactions

            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_not_found()
            ).get(create_user_response.id)

            assert create_account1_response.balance == 0.0
            assert not create_account1_response.transactions

            deposit_amount = RandomData.get_deposit_amount(100.0, 100000.0)
            deposit_request = DepositRequest(id=create_account1_response.id, balance=deposit_amount)
            deposit_response = DepositRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.request_return_ok()
            ).post(deposit_request)

            assert deposit_response.balance == deposit_amount

            get_account_response_after_deposit = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.request_return_ok()
            ).get()

            assert get_account_response_after_deposit.balance == deposit_amount

            transfer_amount = deposit_amount * 0.5
            transfer_request = TransferRequest(
                senderAccountId=create_account1_response.id,
                receiverAccountId=create_account2_response.id,
                amount=transfer_amount
            )
            transfer_response = TransferRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.request_return_ok()
            ).post(transfer_request)

            assert transfer_response.message == "Transfer successful"
            assert transfer_response.senderAccountId == create_account1_response.id
            assert transfer_response.receiverAccountId == create_account2_response.id
            assert transfer_response.amount == transfer_amount

            get_account1_after_transfer = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.request_return_ok()
            ).get(create_account1_response.id)

            get_account2_after_transfer = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.request_return_ok()
            ).get(create_account2_response.id)

        finally:
            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_deleted()
            ).delete(create_user_response.id)

