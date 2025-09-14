from src.main.api.models.base_model import BaseModel

from typing import Optional, List, Dict, Any


class CreateAccountResponse(BaseModel):
    id: int
    accountNumber: str
    balance: float
    transactions: List




