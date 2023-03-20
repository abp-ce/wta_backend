from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

engine = create_async_engine(
    "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
        settings.postgres_user,
        settings.postgres_password,
        settings.postgres_host,
        settings.postgres_port,
        settings.postgres_db,
    ),
    echo=True,
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
