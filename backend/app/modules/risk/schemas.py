from pydantic import BaseModel


class RiskCheckRequest(BaseModel):
    url: str
    # Omitted (None) for passive checks (e.g. the content script's page-load
    # check, or the popup's own first check before it knows whether a warning
    # dialog is even needed). Set to True/False only when this call is
    # logging the outcome of the extension's risk-confirmation dialog.
    proceeded_despite_warning: bool | None = None


class RiskCheckResult(BaseModel):
    ssl_valid: bool
    lookalike_score: float
    risk_score: float
    is_high_risk: bool
    reason_code: str
    explanation: str
