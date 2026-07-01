"""Maps trust_events.reason_code values to plain-language sentences.

Kept backend-driven so the dashboard only ever displays text the API returns,
rather than hardcoding copies of these sentences in the frontend.
"""

EXPLANATIONS = {
    "lookalike_domain": "This site's address looks similar to a known site but isn't identical — a common phishing trick.",
    "ssl_invalid": "This site's security certificate is missing or invalid.",
    "idle_timeout": "Your session has been inactive for a while, so we're increasing security checks.",
    "low_match_score": "Your face didn't match closely enough with your enrolled photo.",
    "healthy": "All signals look normal — identity, site, and activity checks are healthy.",
    "session_start": "Session started after a successful identity verification.",
}

DEFAULT_EXPLANATION = "Trust score updated based on the latest signals."


def explain(reason_code: str) -> str:
    return EXPLANATIONS.get(reason_code, DEFAULT_EXPLANATION)
