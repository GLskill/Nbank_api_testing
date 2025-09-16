from pydantic import BaseModel


class TransferRequest(BaseModel):
    senderAccountId: int
    receiverAccountId: int
    amount: float

    