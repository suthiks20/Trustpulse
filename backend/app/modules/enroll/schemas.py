from pydantic import BaseModel


class EnrollResult(BaseModel):
    card_id: str
    status: str
