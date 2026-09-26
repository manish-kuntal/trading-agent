from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

_engine       = None
_SessionLocal = None


def _init():
    global _engine, _SessionLocal
    if _engine is not None:
        return
    from config.settings import settings
    from agent.db.models import Base
    _engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=True)
    Base.metadata.create_all(bind=_engine)


@contextmanager
def get_session():
    """Use in agent code:  with get_session() as db: ..."""
    _init()
    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    """FastAPI dependency:  db: Session = Depends(get_db)"""
    _init()
    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
