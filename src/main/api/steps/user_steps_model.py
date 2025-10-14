from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.deposit_response import DepositResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponses
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.requests.transfer_requester import TransferRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def login(self, user_request: CreateUserRequest) -> LoginUserResponses:
        login_request = LoginUserRequest(username=user_request.username, password=user_request.password)
        login_response: LoginUserResponses = ValidatedCrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.LOGIN_USER,
            ResponseSpecs.request_return_ok()
        ).post(login_request)
        ModelAssertions(login_request, login_response).match()
        return login_response

    def create_account(self, user_request: CreateUserRequest) -> CreateAccountResponse:
        create_account_response: CreateAccountResponse = ValidatedCrudRequester(
            RequestSpecs.user_auth_spec(user_request.username, user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.entity_was_created()
        ).post()
        assert create_account_response.balance == 0.0
        assert not create_account_response.transactions
        return create_account_response

    def get_all_customer_accounts(self, user_request: CreateUserRequest):
        customers_response = ValidatedCrudRequester(
            RequestSpecs.user_auth_spec(user_request.username, user_request.password),
            Endpoint.GET_CUSTOMER_ACCOUNTS,
            ResponseSpecs.request_return_ok()
        ).get_all()
        return customers_response

    def get_account_by_id(self, account_id: int, user_request: CreateUserRequest) -> CreateAccountResponse:
        response = self.get_all_customer_accounts(user_request)
        accounts = response.json()
        for account_data in accounts:
            if account_data.get('id') == account_id:
                return CreateAccountResponse.model_validate(account_data)
        raise ValueError(f"Account with id {account_id} not found in customer accounts")

    def deposit_to_account(self, user_request: CreateUserRequest, deposit_request: DepositRequest) -> DepositResponse:
        deposit_response: DepositResponse = ValidatedCrudRequester(
            RequestSpecs.user_auth_spec(user_request.username, user_request.password),
            Endpoint.DEPOSIT_ACCOUNT,
            ResponseSpecs.request_return_ok()
        ).post(deposit_request)
        assert deposit_response.balance == deposit_request.balance
        return deposit_response

    def transfer_money(self, transfer_request: TransferRequest, user_request: CreateUserRequest) -> TransferResponse:
        transfer_response: TransferResponse = TransferRequester(
            RequestSpecs.user_auth_spec(user_request.username, user_request.password),
            ResponseSpecs.request_return_ok()
        ).post(transfer_request)
        self.created_objects.append(transfer_response)
        return transfer_response


