"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    # Gemini API
    GEMINI_API_KEY: str = "your_gemini_api_key_here"
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Database - supports both SQLite (local) and PostgreSQL (cloud)
    DATABASE_URL: str = ""  # PostgreSQL URL for cloud (e.g. Render)
    DB_PATH: str = "../data/db/copilot.db"  # SQLite path for local

    # Data directories
    DATA_DIR: str = "../data"

    # Scraper settings
    SCRAPE_DELAY_MIN: int = 2
    SCRAPE_DELAY_MAX: int = 5
    MIN_MATCH_SCORE: float = 0.62

    # Server
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # CORS - comma-separated allowed origins for production
    CORS_ORIGINS: str = ""

    @property
    def db_url(self) -> str:
        """SQLAlchemy database URL."""
        # Use DATABASE_URL if set (cloud PostgreSQL)
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            # Render uses postgres:// but SQLAlchemy needs postgresql://
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url

        # Fallback to SQLite for local development
        db_path = Path(self.DB_PATH)
        if not db_path.is_absolute():
            db_path = Path(__file__).parent / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path.resolve()}"

    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL."""
        return bool(self.DATABASE_URL)

    @property
    def data_path(self) -> Path:
        """Resolved data directory path."""
        p = Path(self.DATA_DIR)
        if not p.is_absolute():
            p = Path(__file__).parent / p
        p = p.resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins for production."""
        defaults = [
            "http://localhost:3000",
            "http://localhost:5173",
        ]
        if self.FRONTEND_URL:
            defaults.append(self.FRONTEND_URL.rstrip('/'))
        if self.CORS_ORIGINS:
            defaults.extend([o.strip().rstrip('/') for o in self.CORS_ORIGINS.split(",") if o.strip()])
        return list(set(defaults)) # Unique set of origins

    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"


settings = Settings()
