import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.requests.admin_user_requester import AdminUserRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.deposit_reqester import DepositRequester
from src.main.api.requests.transfer_requester import TransferRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestTransfer:
    @pytest.mark.parametrize(
        "username, password, role",
        [(RandomData.get_username(), RandomData.get_password(), 'USER'), ]
    )
    def test_transfer_successful(self, username: str, password: str, role: str):
        create_user1_request = CreateUserRequest(username=username, password=password, role=role)

        create_user1_response = AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_created()
        ).post(create_user1_request)

        assert create_user1_response.username == create_user1_request.username
        assert create_user1_response.role == create_user1_request.role

        create_user2_request = CreateUserRequest(username=username, password=password, role=role)

        create_user2_response = AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_created()
        ).post(create_user1_request)

        assert create_user2_response.username == create_user2_request.username
        assert create_user2_response.role == create_user2_request.role

        try:
            create_account1_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user1_request.username, create_user1_request.password),
                ResponseSpecs.entity_was_created()
            ).post()

            assert create_account1_response.balance == 0.0
            assert not create_account1_response.transactions

            get_account1_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user1_request.username, create_user1_request.password),
                ResponseSpecs.request_return_ok()
            ).get()

            assert create_account1_response.balance == 0.0
            assert not create_account1_response.transactions

            # Create account for second user
            create_account2_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user2_request.username, create_user2_request.password),
                ResponseSpecs.entity_was_created()
            ).post()

            assert create_account2_response.balance == 0.0
            assert not create_account2_response.transactions

            get_account2_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user2_request.username, create_user2_request.password),
                ResponseSpecs.request_return_ok()
            ).get()

            assert create_account2_response.balance == 0.0
            assert not create_account2_response.transactions

            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_not_found()
            ).get(create_user1_response.id)

            assert create_account1_response.balance == 0.0
            assert not create_account1_response.transactions

            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_not_found()
            ).get(create_user2_response.id)

            assert create_account2_response.balance == 0.0
            assert not create_account2_response.transactions

            deposit_amount = RandomData.get_deposit_amount(100.0, 100000.0)
            deposit_request = DepositRequest(id=create_account1_response.id, balance=deposit_amount)
            deposit_response = DepositRequester(
                RequestSpecs.user_auth_spec(create_user1_request.username, create_user1_request.password),
                ResponseSpecs.request_return_ok()
            ).post(deposit_request)

            assert deposit_response.balance == deposit_amount
            assert any(
                transaction.type == "DEPOSIT" and transaction.amount == deposit_amount
                for transaction in deposit_response.transactions
            )

            get_account1_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user1_request.username, create_user1_request.password),
                ResponseSpecs.request_return_ok()
            ).get()

            assert deposit_response.balance == deposit_amount
            assert any(
                transaction.type == "DEPOSIT" and transaction.amount == deposit_amount
                for transaction in deposit_response.transactions
            )

            transfer_amount = deposit_amount * 0.5
            transfer_request = TransferRequest(
                senderAccountId=create_account1_response.id,
                receiverAccountId=create_account2_response.id,
                amount=transfer_amount
            )

            transfer_response = TransferRequester(
                RequestSpecs.user_auth_spec(create_user1_request.username, create_user1_request.password),
                ResponseSpecs.request_return_ok()
            ).post(transfer_request)

            assert transfer_response.message == "Transfer successful"
            assert transfer_response.senderAccountId == create_account1_response.id
            assert transfer_response.receiverAccountId == create_account2_response.id
            assert transfer_response.amount == transfer_amount

            get_account1_after_transfer = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user1_request.username, create_user1_request.password),
                ResponseSpecs.request_return_ok()
            ).get()

            assert get_account1_after_transfer.balance == deposit_amount - transfer_amount
            assert any(
                transaction.type == "TRANSFER_OUT" and transaction.amount == transfer_amount
                for transaction in get_account1_after_transfer.transactions
            )

            get_account2_after_transfer = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user2_request.username, create_user2_request.password),
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
            ).delete(create_user1_response.id)
            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_deleted()
            ).delete(create_user2_response.id)
