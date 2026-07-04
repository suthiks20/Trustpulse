from datetime import datetime

from pydantic import BaseModel


class TrustEventOut(BaseModel):
    event_id: int
    session_id: str
    timestamp: datetime
    signal_type: str
    signal_value: float
    resulting_score: float
    reason_code: str
    explanation: str
