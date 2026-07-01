from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session as OrmSession

from app.db.models import AuthLog, DemoCard, SiteRiskCheck, Session, TrustEvent


def utcnow():
    return datetime.now(timezone.utc)


def next_card_id(db: OrmSession) -> str:
    count = db.query(DemoCard).count()
    return f"DC{count + 1:04d}"


def create_demo_card(db: OrmSession, card_id: str, name: str, dob: str, photo_path: str, embedding: bytes) -> DemoCard:
    card = DemoCard(card_id=card_id, name=name, dob=dob, photo_path=photo_path, embedding=embedding)
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def get_demo_card(db: OrmSession, card_id: str) -> DemoCard | None:
    return db.query(DemoCard).filter(DemoCard.card_id == card_id).first()


def get_all_cards(db: OrmSession) -> list[DemoCard]:
    return db.query(DemoCard).order_by(desc(DemoCard.enrolled_at)).all()


def create_auth_log(db: OrmSession, card_id: str, match_score: float, liveness_passed: bool, result: str) -> AuthLog:
    log = AuthLog(card_id=card_id, match_score=match_score, liveness_passed=liveness_passed, result=result)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_latest_auth_log(db: OrmSession, card_id: str) -> AuthLog | None:
    return (
        db.query(AuthLog)
        .filter(AuthLog.card_id == card_id)
        .order_by(desc(AuthLog.timestamp))
        .first()
    )


def get_auth_logs(db: OrmSession, limit: int = 20) -> list[AuthLog]:
    return db.query(AuthLog).order_by(desc(AuthLog.timestamp)).limit(limit).all()


def create_session(db: OrmSession, session_id: str, card_id: str) -> Session:
    session = Session(session_id=session_id, card_id=card_id, trust_score=100.0)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: OrmSession, session_id: str) -> Session | None:
    return db.query(Session).filter(Session.session_id == session_id).first()


def get_all_sessions(db: OrmSession) -> list[Session]:
    return db.query(Session).order_by(desc(Session.issued_at)).all()


def update_session_heartbeat(db: OrmSession, session: Session, trust_score: float) -> Session:
    session.last_heartbeat = utcnow()
    session.trust_score = trust_score
    session.last_score_update = utcnow()
    db.commit()
    db.refresh(session)
    return session


def create_site_risk_check(
    db: OrmSession, url: str, ssl_valid: bool, lookalike_score: float, risk_score: float
) -> SiteRiskCheck:
    check = SiteRiskCheck(url=url, ssl_valid=ssl_valid, lookalike_score=lookalike_score, risk_score=risk_score)
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


def get_latest_risk_check(db: OrmSession) -> SiteRiskCheck | None:
    return db.query(SiteRiskCheck).order_by(desc(SiteRiskCheck.checked_at)).first()


def get_risk_checks(db: OrmSession, limit: int = 20) -> list[SiteRiskCheck]:
    return db.query(SiteRiskCheck).order_by(desc(SiteRiskCheck.checked_at)).limit(limit).all()


def create_trust_event(
    db: OrmSession,
    session_id: str,
    signal_type: str,
    signal_value: float,
    resulting_score: float,
    reason_code: str,
) -> TrustEvent:
    event = TrustEvent(
        session_id=session_id,
        signal_type=signal_type,
        signal_value=signal_value,
        resulting_score=resulting_score,
        reason_code=reason_code,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_trust_events(db: OrmSession, session_id: str) -> list[TrustEvent]:
    return (
        db.query(TrustEvent)
        .filter(TrustEvent.session_id == session_id)
        .order_by(TrustEvent.timestamp)
        .all()
    )
