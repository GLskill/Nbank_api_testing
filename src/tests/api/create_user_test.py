import pytest

from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.requests.admin_user_requester import AdminUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestCreateUser:
    def test_create_valid_user(self):
        create_user_request = CreateUserRequest(username=RandomData.get_username(),
                                                password=RandomData.get_password(), role='USER')
        create_user_response = AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_created()
        ).post(create_user_request)

        assert create_user_response.username == create_user_request.username
        assert create_user_response.role == create_user_request.role

        AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.entity_was_deleted()
        ).delete(create_user_response.id)

    @pytest.mark.parametrize(
        argnames='username, password, role, error_key, error_value',
        argvalues=[
            (' ', RandomData.get_password(), 'USER', 'username', 'Username must contain only letters'),
            ('Vlasv_@1201', RandomData.get_password(), 'USER', 'username',
             'Username must contain only letters, digits, dashes, underscores, and dots'),
            ('gl', RandomData.get_password(), 'USER', 'username', 'Username must be between 3 and 15 characters'),
            ('gliutjolfjuicbjt', RandomData.get_password(), 'USER', 'username',
             'Username must be between 3 and 15 characters')
        ]
    )
    def test_create_invalid_user(self, username: str, password: str, role: str, error_key: str, error_value: str):
        create_user_request = CreateUserRequest(username=username, password=password, role=role)

        AdminUserRequester(
            RequestSpecs.admin_auth_spec(),
            ResponseSpecs.request_return_bad_request(error_key, error_value)
        ).post(create_user_request)

