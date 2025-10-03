from typing import Optional

from src.main.api.models.base_model import BaseModel


class LoginUserResponses(BaseModel):
    username: str
    role: str
    token: Optional[str] = None

