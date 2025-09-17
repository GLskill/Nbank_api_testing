from pydantic import BaseModel


class TransferResponse(BaseModel):
    message: str
    senderAccountId: int
    receiverAccountId: int
    amount: float

