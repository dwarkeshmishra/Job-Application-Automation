"""
Job Application Copilot — FastAPI Backend Entry Point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from database import init_db
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Job Application Copilot API...")
    init_db()
    logger.info("Database tables initialized.")
    try:
        from scheduler.pipeline import start_scheduler
        start_scheduler()
    except Exception as e:
        logger.warning(f"Scheduler not started: {e}")
    yield
    logger.info("Shutting down Job Application Copilot API.")


app = FastAPI(
    title="Job Application Copilot API",
    description="AI-powered job application system with resume tailoring, ATS scoring, and job tracking.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated data files
data_dir = settings.data_path
if data_dir.exists():
    app.mount("/api/files", StaticFiles(directory=str(data_dir)), name="data")

# Register routers
try:
    from routers import profile, jobs, scraper, resume, score, tracker, analyze, export_router
    app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
    app.include_router(scraper.router, prefix="/api/scrape", tags=["Scraper"])
    app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
    app.include_router(score.router, prefix="/api/score", tags=["ATS Score"])
    app.include_router(tracker.router, prefix="/api/tracker", tags=["Tracker"])
    app.include_router(analyze.router, prefix="/api/analyze", tags=["Analyze"])
    app.include_router(export_router.router, prefix="/api/export", tags=["Export"])
    logger.info("All routers registered.")
except ImportError as e:
    logger.warning(f"Some routers not loaded: {e}")


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "running",
        "service": "Job Application Copilot API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "postgresql" if settings.is_postgres else "sqlite",
        "llm_provider": "gemini",
        "model": settings.GEMINI_MODEL,
    }
