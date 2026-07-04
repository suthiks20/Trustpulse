from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.modules.trust import trust_engine
from app.shared.models import Session as SessionModel


def make_session(last_heartbeat: datetime, card_id: str = "DC0001", session_id: str = "sess-1") -> SessionModel:
    return SessionModel(session_id=session_id, card_id=card_id, last_heartbeat=last_heartbeat, trust_score=100.0)


def auth_log(match_score: float):
    return SimpleNamespace(match_score=match_score)


def risk_check(ssl_valid: bool, lookalike_score: float, risk_score: float):
    return SimpleNamespace(ssl_valid=ssl_valid, lookalike_score=lookalike_score, risk_score=risk_score)


def test_constants_are_unchanged():
    # These exact values are load-bearing for every client (dashboard badge
    # colors, extension badge colors) — regressions here silently desync them.
    assert trust_engine.IDLE_MAX_SECONDS == 60.0
    assert trust_engine.WARNING_THRESHOLD == 60.0
    assert trust_engine.REVERIFY_IMMEDIATE_THRESHOLD == 35.0


async def _compute(session, auth_log_value=None, risk_check_value=None, trust_events=None):
    with (
        patch.object(trust_engine, "get_latest_auth_log", AsyncMock(return_value=auth_log_value)),
        patch.object(trust_engine, "get_latest_risk_check", AsyncMock(return_value=risk_check_value)),
        patch.object(trust_engine.trust_repository, "create_trust_event", AsyncMock()),
        patch.object(trust_engine.trust_repository, "get_trust_events", AsyncMock(return_value=trust_events or [])),
    ):
        return await trust_engine.compute_trust_score(db=None, session=session)


async def test_healthy_session_scores_100():
    session = make_session(last_heartbeat=trust_engine.utcnow())
    result = await _compute(session)

    # A few ms elapse between building the session and compute_trust_score's
    # own utcnow() call, so behavior decays by a hair — assert "effectively 100".
    assert result["trust_score"] == pytest.approx(100.0, abs=0.1)
    assert result["flag"] == "none"
    assert result["reason_code"] == "healthy"


async def test_idle_behavior_degrades_score_but_stays_healthy():
    session = make_session(last_heartbeat=trust_engine.utcnow() - timedelta(seconds=30))
    result = await _compute(session)

    # 0.4*100 + 0.3*100 + 0.2*50 + 0.1*100 = 90.0
    assert result["trust_score"] == 90.0
    assert result["flag"] == "none"
    assert result["reason_code"] == "idle_timeout"


async def test_ssl_invalid_and_dead_session_forces_immediate_reverify():
    session = make_session(last_heartbeat=trust_engine.utcnow() - timedelta(seconds=120))
    result = await _compute(
        session,
        auth_log_value=auth_log(match_score=0.0),
        risk_check_value=risk_check(ssl_valid=False, lookalike_score=0.0, risk_score=100.0),
    )

    # 0.4*0 + 0.3*(100-100) + 0.2*0 + 0.1*100 = 10.0
    assert result["trust_score"] == 10.0
    assert result["flag"] == "reverify"
    assert result["reason_code"] == "ssl_invalid"  # site risk is checked before identity/behavior


async def test_sustained_warning_escalates_to_reverify():
    # Identity + full idle decay lands trust_score at 52 (in the 35-60 "warning"
    # band on its own); prior events below the warning threshold for >15s are
    # what pushes it from "warning" to "reverify".
    session = make_session(last_heartbeat=trust_engine.utcnow() - timedelta(seconds=60))
    now = trust_engine.utcnow()
    prior_events = [
        SimpleNamespace(resulting_score=50.0, timestamp=now - timedelta(seconds=20)),
        SimpleNamespace(resulting_score=55.0, timestamp=now - timedelta(seconds=10)),
    ]

    result = await _compute(session, auth_log_value=auth_log(match_score=0.3), trust_events=prior_events)

    assert result["trust_score"] == 52.0
    assert result["flag"] == "reverify"


def test_is_session_expired_past_idle_window():
    session = make_session(last_heartbeat=trust_engine.utcnow() - timedelta(seconds=61))
    assert trust_engine.is_session_expired(session) is True


def test_is_session_expired_within_idle_window():
    session = make_session(last_heartbeat=trust_engine.utcnow() - timedelta(seconds=59))
    assert trust_engine.is_session_expired(session) is False
