from app.db import models  # noqa: F401  (ensures models are registered on Base)
from app.db.database import Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print(f"Tables created: {list(Base.metadata.tables.keys())}")
