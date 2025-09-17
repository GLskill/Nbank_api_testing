import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.requests.admin_user_requester import AdminUserRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestCreateAccount:
    @pytest.mark.parametrize(
        "username, password, role",
        [(RandomData.get_username(), RandomData.get_password(), 'USER'), ]
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
            create_account_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.entity_was_created()
            ).post()

            assert create_account_response.balance == 0.0
            assert not create_account_response.transactions

            get_account_response = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username, create_user_request.password),
                ResponseSpecs.request_return_ok()
            ).get()

            assert create_account_response.balance == 0.0
            assert not create_account_response.transactions

            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_not_found()
            ).get(create_user_response.id)

            assert create_account_response.balance == 0.0
            assert not create_account_response.transactions

            invalid_username_requester = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username + RandomData.get_username(),
                                            create_user_request.password),
                ResponseSpecs.request_return_unauth("error", "Invalid username or password")
            )
            invalid_username_requester.post()

            invalid_password_requester = CreateAccountRequester(
                RequestSpecs.user_auth_spec(create_user_request.username,
                                            create_user_request.password + RandomData.get_password()),
                ResponseSpecs.request_return_unauth("error", "Invalid username or password")
            )
            invalid_password_requester.post()

        finally:
            AdminUserRequester(
                RequestSpecs.admin_auth_spec(),
                ResponseSpecs.entity_was_deleted()
            ).delete(create_user_response.id)
