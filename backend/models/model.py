from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    message: str


class ValidateRequest(BaseModel):
    payment_id: str
    order_id: str
    razor_signature: str

class QRRequest(BaseModel):
    ticket_id: str