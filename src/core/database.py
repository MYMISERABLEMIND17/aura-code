from src.core.config import settings

_engine = None
_async_session_maker = None

def get_engine():
    global _engine, _async_session_maker
    if _engine is None:
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
            _engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=5, max_overflow=5)
            _async_session_maker = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
        except Exception:
            _engine = None
    return _engine

async def get_db():
    get_engine()
    if _async_session_maker is not None:
        async with _async_session_maker() as session:
            yield session
    else:
        yield None
