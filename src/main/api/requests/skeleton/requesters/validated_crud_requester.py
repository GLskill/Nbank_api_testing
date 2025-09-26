from typing import TypeVar, Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.requests.skeleton.http_request import HttpRequest
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester

T = TypeVar('T', bound=BaseModel)


class ValidatedCrudRequester(HttpRequest):
    def __init__(self, request_spec, endpoint, response_spec):
        super().__init__(request_spec, endpoint, response_spec)
        self.crud_requester = CrudRequester(
            request_spec=request_spec,
            endpoint=endpoint,
            response_spec=response_spec
        )

    def post(self, model: Optional[BaseModel] = None):
        response = self.crud_requester.post(model)
        return self.endpoint.value.response_model.model_validate(response.json())

    def get(self, id: int): ...
    def update(self, id: int): ...
    def delete(self, id: int): ...


