from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import get_settings

# asyncpg speaks the wire protocol directly and doesn't understand libpq-style
# query params like sslmode/channel_binding — drop them and rely on asyncpg's
# default (which negotiates TLS with Neon automatically over the pooler).
_DROP_QUERY_PARAMS = {"sslmode", "channel_binding"}


def _to_asyncpg_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg://"):
        url = raw_url
    elif raw_url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + raw_url[len("postgresql://") :]
    else:
        url = raw_url

    parts = urlsplit(url)
    filtered_query = [(k, v) for k, v in parse_qsl(parts.query) if k not in _DROP_QUERY_PARAMS]
    return urlunsplit(parts._replace(query=urlencode(filtered_query)))


settings = get_settings()

engine = create_async_engine(_to_asyncpg_url(settings.DATABASE_URL), pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
