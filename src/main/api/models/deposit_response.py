from src.main.api.models.base_model import BaseModel
from typing import List


class Transactions(BaseModel):
    id: int
    amount: float
    type: str
    timestamp: str
    relatedAccountId: int


class DepositResponse(BaseModel):
    id: int
    accountNumber: str
    balance: float
    transactions: List[Transactions]



