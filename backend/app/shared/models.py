from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import relationship

from app.shared.database import Base


def utcnow():
    # Columns are TIMESTAMP WITHOUT TIME ZONE in Neon; asyncpg (unlike the old
    # psycopg2 driver) rejects tz-aware values against that column type, so
    # store naive UTC wall-clock time here.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class DemoCard(Base):
    __tablename__ = "demo_cards"

    card_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    dob = Column(String, nullable=False)
    photo_path = Column(String, nullable=False)
    embedding = Column(LargeBinary, nullable=False)
    enrolled_at = Column(DateTime, default=utcnow)

    auth_logs = relationship("AuthLog", back_populates="card")
    sessions = relationship("Session", back_populates="card")


class AuthLog(Base):
    __tablename__ = "auth_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey("demo_cards.card_id"), nullable=False)
    timestamp = Column(DateTime, default=utcnow)
    match_score = Column(Float, nullable=False)
    liveness_passed = Column(Boolean, nullable=False)
    result = Column(String, nullable=False)  # "success" | "fail"

    card = relationship("DemoCard", back_populates="auth_logs")


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)
    card_id = Column(String, ForeignKey("demo_cards.card_id"), nullable=False)
    issued_at = Column(DateTime, default=utcnow)
    last_heartbeat = Column(DateTime, default=utcnow)
    trust_score = Column(Float, default=100.0)
    last_score_update = Column(DateTime, default=utcnow)

    card = relationship("DemoCard", back_populates="sessions")
    trust_events = relationship("TrustEvent", back_populates="session")


class SiteRiskCheck(Base):
    __tablename__ = "site_risk_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    ssl_valid = Column(Boolean, nullable=False)
    lookalike_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    checked_at = Column(DateTime, default=utcnow)
    # NULL for passive checks (e.g. the content script's page-load check) where
    # no user ever saw a warning; True/False only for the ones logged from the
    # extension's login risk-confirmation dialog.
    proceeded_despite_warning = Column(Boolean, nullable=True)


class TrustEvent(Base):
    __tablename__ = "trust_events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    timestamp = Column(DateTime, default=utcnow)
    signal_type = Column(String, nullable=False)  # "identity" | "site" | "behavior"
    signal_value = Column(Float, nullable=False)
    resulting_score = Column(Float, nullable=False)
    reason_code = Column(String, nullable=False)

    session = relationship("Session", back_populates="trust_events")
