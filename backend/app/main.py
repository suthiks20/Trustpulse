import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.modules.auth.routes import router as auth_router
from app.modules.dashboard.routes import router as dashboard_router
from app.modules.enroll.routes import router as enroll_router
from app.modules.risk.routes import router as risk_router
from app.modules.session.routes import router as session_router
from app.modules.trust.routes import router as trust_router
from app.modules.verify.routes import router as verify_router
from app.shared.database import engine
from app.shared.exceptions import register_exception_handlers
from app.shared.logging import RequestContextMiddleware, configure_logging, logger
from app.shared.rate_limit import limiter
from app.shared.schemas import ok

settings = get_settings()

if sys.platform == "win32":
    # ProactorEventLoop's SSL transport races asyncpg's connection teardown on
    # shutdown (harmless but noisy); Selector doesn't have that issue.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("startup_db_connected", env=settings.ENV)
    yield
    await engine.dispose()


app = FastAPI(title="TrustPulse", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: _rate_limit_response(exc))
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


def _rate_limit_response(exc: RateLimitExceeded):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=429,
        content={"success": False, "data": None, "error": {"code": "rate_limited", "message": str(exc.detail)}},
    )


app.include_router(auth_router)
app.include_router(enroll_router)
app.include_router(verify_router)
app.include_router(session_router)
app.include_router(risk_router)
app.include_router(trust_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return ok({"status": "ok", "service": "TrustPulse"})


@app.get("/health")
async def health():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return ok({"status": "ok", "db": "connected"})
