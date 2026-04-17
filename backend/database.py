"""SQLAlchemy database setup and session management."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

connect_args = {}
if not settings.is_postgres:
    connect_args["check_same_thread"] = False  # SQLite needs this

engine = create_engine(
    settings.db_url,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,  # Helps with cloud DB connection drops
)

# Enable WAL mode and foreign keys for SQLite only
if not settings.is_postgres:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Create all tables if they don't exist."""
    from models import user_profile, job, application, skill, scrape_run  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI route injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
