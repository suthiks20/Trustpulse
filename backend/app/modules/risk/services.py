from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.modules.risk import repository
from app.modules.risk.url_checker import check_url
from app.modules.trust.explain import explain


def is_high_risk(risk_score: float, ssl_valid: bool) -> bool:
    settings = get_settings()
    return (not ssl_valid) or (risk_score >= settings.RISK_WARNING_THRESHOLD)


def _reason_code(ssl_valid: bool, lookalike_score: float) -> str:
    # Mirrors trust_engine._site_risk's precedence (ssl before lookalike) so
    # the same signal always maps to the same reason_code everywhere it's
    # surfaced — in a trust_event, or here in a risk-check response.
    if not ssl_valid:
        return "ssl_invalid"
    if lookalike_score >= 50:
        return "lookalike_domain"
    return "healthy"


async def run_risk_check(db: AsyncSession, url: str, proceeded_despite_warning: bool | None = None) -> dict:
    result = check_url(url)
    ssl_valid = result["ssl_valid"]
    lookalike_score = result["lookalike_score"]
    risk_score = result["risk_score"]

    await repository.create_site_risk_check(
        db,
        url=url,
        ssl_valid=ssl_valid,
        lookalike_score=lookalike_score,
        risk_score=risk_score,
        proceeded_despite_warning=proceeded_despite_warning,
    )

    reason_code = _reason_code(ssl_valid, lookalike_score)

    return {
        "ssl_valid": ssl_valid,
        "lookalike_score": lookalike_score,
        "risk_score": risk_score,
        "is_high_risk": is_high_risk(risk_score, ssl_valid),
        "reason_code": reason_code,
        "explanation": explain(reason_code),
    }
