"""Dashboard owns no tables of its own — it's a read-only reporting layer over
the tables owned by enroll/verify/session/risk/trust. Re-export their async
queries here so services.py has a single DB-access surface to depend on.
"""

from app.modules.enroll.repository import get_all_cards
from app.modules.risk.repository import get_risk_checks
from app.modules.session.repository import get_all_sessions, get_session, get_sessions_for_card
from app.modules.trust.repository import get_trust_events, get_trust_events_for_card
from app.modules.verify.repository import get_auth_logs, get_auth_logs_for_card, get_demo_card

__all__ = [
    "get_all_cards",
    "get_risk_checks",
    "get_all_sessions",
    "get_session",
    "get_sessions_for_card",
    "get_trust_events",
    "get_trust_events_for_card",
    "get_auth_logs",
    "get_auth_logs_for_card",
    "get_demo_card",
]
