from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


class UserSteps:
    @staticmethod
    def create_account(username: str, password: str):
        return CreateAccountRequester(
            RequestSpecs.user_auth_spec(username, password),
            ResponseSpecs.entity_was_created()
        ).post()
