"""Fuses identity, site-risk, and behavior signals into one continuous Trust Score.

trust_score = 0.4 * identity_confidence
            + 0.3 * (100 - site_risk)
            + 0.2 * behavior_score
            + 0.1 * environment_score
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.risk.repository import get_latest_risk_check
from app.modules.trust import repository as trust_repository
from app.modules.verify.repository import get_latest_auth_log
from app.shared.logging import logger
from app.shared.models import Session as SessionModel

IDLE_MAX_SECONDS = 60.0
WARNING_THRESHOLD = 60.0
REVERIFY_IMMEDIATE_THRESHOLD = 35.0
SUSTAINED_WARNING_SECONDS = 15.0

# placeholder — not implemented in this demo, see README limitations
ENVIRONMENT_SCORE = 100.0


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def is_session_expired(session: SessionModel, now: datetime | None = None) -> bool:
    now = now or utcnow()
    idle_seconds = (now - _aware(session.last_heartbeat)).total_seconds()
    return idle_seconds > IDLE_MAX_SECONDS


async def _identity_confidence(db: AsyncSession, card_id: str) -> tuple[float, str | None]:
    log = await get_latest_auth_log(db, card_id)
    if log is None:
        return 100.0, None
    score = log.match_score * 100
    reason = "low_match_score" if score < 65 else None
    return score, reason


async def _site_risk(db: AsyncSession) -> tuple[float, str | None]:
    check = await get_latest_risk_check(db)
    if check is None:
        return 0.0, None
    if not check.ssl_valid:
        return check.risk_score, "ssl_invalid"
    if check.lookalike_score >= 50:
        return check.risk_score, "lookalike_domain"
    return check.risk_score, None


def _behavior_score(last_heartbeat: datetime, now: datetime) -> tuple[float, str | None]:
    idle_seconds = max(0.0, (now - _aware(last_heartbeat)).total_seconds())
    score = max(0.0, 100.0 - (idle_seconds / IDLE_MAX_SECONDS) * 100.0)
    reason = "idle_timeout" if score < 70 else None
    return score, reason


async def _sustained_low_duration(db: AsyncSession, session_id: str, now: datetime) -> float:
    events = await trust_repository.get_trust_events(db, session_id)
    start = None
    for event in reversed(events):
        if event.resulting_score < WARNING_THRESHOLD:
            start = event.timestamp
        else:
            break
    if start is None:
        return 0.0
    return (now - _aware(start)).total_seconds()


async def compute_trust_score(db: AsyncSession, session: SessionModel) -> dict:
    now = utcnow()

    id_score, id_reason = await _identity_confidence(db, session.card_id)
    site_score, site_reason = await _site_risk(db)
    behav_score, behav_reason = _behavior_score(session.last_heartbeat, now)

    trust_score = (
        0.4 * id_score
        + 0.3 * (100 - site_score)
        + 0.2 * behav_score
        + 0.1 * ENVIRONMENT_SCORE
    )
    trust_score = round(max(0.0, min(100.0, trust_score)), 2)

    if site_reason:
        reason_code, signal_type, signal_value = site_reason, "site", site_score
    elif id_reason:
        reason_code, signal_type, signal_value = id_reason, "identity", id_score
    elif behav_reason:
        reason_code, signal_type, signal_value = behav_reason, "behavior", behav_score
    else:
        reason_code, signal_type, signal_value = "healthy", "behavior", behav_score

    await trust_repository.create_trust_event(
        db,
        session_id=session.session_id,
        signal_type=signal_type,
        signal_value=signal_value,
        resulting_score=trust_score,
        reason_code=reason_code,
    )

    sustained_duration = await _sustained_low_duration(db, session.session_id, now)

    if trust_score < REVERIFY_IMMEDIATE_THRESHOLD:
        flag = "reverify"
    elif trust_score < WARNING_THRESHOLD and sustained_duration > SUSTAINED_WARNING_SECONDS:
        flag = "reverify"
    elif trust_score < WARNING_THRESHOLD:
        flag = "warning"
    else:
        flag = "none"

    logger.info(
        "trust_score_computed",
        session_id=session.session_id,
        card_id=session.card_id,
        trust_score=trust_score,
        flag=flag,
        reason_code=reason_code,
    )

    return {"trust_score": trust_score, "flag": flag, "reason_code": reason_code}
