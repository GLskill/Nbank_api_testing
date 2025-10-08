import logging

import requests

from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.specs.response_specs import ResponseSpecs


class RequestSpecs:
    @staticmethod
    def default_req_headers():
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    @staticmethod
    def unauth_spec():
        return RequestSpecs.default_req_headers()

    @staticmethod
    def admin_auth_spec():
        headers = RequestSpecs.default_req_headers()
        headers['Authorization'] = 'Basic YWRtaW46YWRtaW4='
        return headers

    @staticmethod
    def user_auth_spec(username: str, password: str):
        try:
            response: requests.Response = CrudRequester(
                RequestSpecs.unauth_spec(),
                Endpoint.LOGIN_USER,
                ResponseSpecs.request_return_ok()
            ).post(LoginUserRequest(username=username, password=password))
        except:
            logging.error(f"Authentication failed for {username} with status {response.status_code}")
            raise Exception("Failed to authenticate user")
        else:
            auth_header = response.headers.get("Authorization")
            headers = RequestSpecs.default_req_headers()
            headers["Authorization"] = auth_header
            return headers


