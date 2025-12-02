from src.main.api.helpers.allure_helpers import allure_step
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class AdminSteps(BaseSteps):
    @allure_step("Create user: {user_request.username} with role {user_request.role}")
    def create_user(self, user_request: CreateUserRequest):
        create_user_response: CreateUserResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.entity_was_created()
        ).post(user_request)
        ModelAssertions(user_request, create_user_response).match()

        self.created_objects.append(create_user_response)

        return create_user_response

    @allure_step("Create invalid user: {user_request.username} (expecting error: {error_key})")
    def create_invalid_user(self, user_request: CreateUserRequest, error_key: str, error_value: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_return_bad_request(error_key, error_value)
        ).post(user_request)

    @allure_step("Get all users")
    def get_all_users(self):
        response = CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_GET_ALL_USER,
            ResponseSpecs.request_return_ok()
        ).get_all()
        return response

    @allure_step("Get user by ID: {user_id}")
    def get_user_by_id(self, user_id: int) -> CreateUserResponse:
        response = self.get_all_users()
        users = response.json()
        for user_data in users:
            if user_data.get('id') == user_id:
                return CreateUserResponse.model_validate(user_data)

        raise ValueError(f"User with id {user_id} not found in users list")

    @allure_step("Delete user: {user_id}")
    def delete_user(self, user_id: int):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_DELETE_USER,
            ResponseSpecs.entity_was_deleted()
        ).delete(user_id)
