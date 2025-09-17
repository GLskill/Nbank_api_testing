import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.requests.admin_user_requester import AdminUserRequester
from src.main.api.requests.login_user_requester import LoginUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestLoginUser:
    @pytest.mark.parametrize(
        "username, password, role",
        [(RandomData.get_username(), RandomData.get_password(), 'USER')]
    )
    def test_login_user(self, username: str, password: str, role: str):
        create_user_request = CreateUserRequest(username=username, password=password, role=role)

        create_user_response = AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_created()
        ).post(create_user_request)

        assert create_user_response.username == create_user_request.username
        assert create_user_response.role == create_user_request.role

        login_user_request = LoginUserRequest(username=username, password=password)
        login_response = LoginUserRequester(
            RequestSpecs.unauth_spec(),
            ResponseSpecs.request_return_ok()
        ).post(login_user_request)

        assert login_response.username == login_user_request.username
        assert login_response.role == create_user_request.role

        AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_deleted()
        ).delete(create_user_response.id)

    def test_login_admin_user(self):
        login_user_request = LoginUserRequest(username='admin', password='admin')
        login_response = LoginUserRequester(
            RequestSpecs.unauth_spec(),
            ResponseSpecs.request_return_ok()
        ).post(login_user_request)

        assert login_response.username == login_user_request.username
        assert login_response.role == 'ADMIN'

