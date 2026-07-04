from pydantic import BaseModel


class SessionStartRequest(BaseModel):
    card_id: str


class SessionHeartbeatRequest(BaseModel):
    session_id: str


class SessionStartResult(BaseModel):
    session_id: str
    trust_score: float
    card_name: str


class SessionHeartbeatResult(BaseModel):
    trust_score: float
    flag: str
    latest_reason: str
