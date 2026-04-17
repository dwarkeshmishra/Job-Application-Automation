"""Scraper router — trigger scrapes, check status."""

import json
import logging
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models.job import Job
from models.user_profile import UserProfile
from models.scrape_run import ScrapeRun
from services.embedding_service import embedder
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory task tracker (for single-user local system)
_scrape_tasks: dict = {}


@router.post("/run")
async def run_scrape(data: dict, db: Session = Depends(get_db)):
    """Start a scraping job in the background."""
    sources = data.get("sources", ["remotive"])
    keywords = data.get("keywords", ["software engineer"])
    location = data.get("location", "india")
    max_per_source = data.get("max_per_source", 25)

    task_id = f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    _scrape_tasks[task_id] = {
        "status": "started",
        "jobs_found": 0,
        "jobs_added": 0,
        "jobs_duplicate": 0,
        "sources_completed": [],
        "errors": [],
    }

    # Run scraping in background
    asyncio.create_task(
        _run_scrape_background(task_id, sources, keywords, location, max_per_source)
    )

    return {
        "task_id": task_id,
        "status": "started",
        "message": f"Scrape running in background. Check /api/scrape/status/{task_id}",
    }


@router.get("/status/{task_id}")
async def scrape_status(task_id: str):
    """Check the status of a scrape task."""
    if task_id not in _scrape_tasks:
        raise HTTPException(404, "Task not found")
    return {"task_id": task_id, **_scrape_tasks[task_id]}


async def _run_scrape_background(task_id: str, sources: list, keywords: list,
                                  location: str, max_per_source: int):
    """Background scrape task."""
    db = SessionLocal()
    started_at = datetime.now()

    try:
        all_jobs = []

        for source in sources:
            try:
                if source == "remotive":
                    from scrapers.remotive_scraper import RemotiveScraper
                    scraper = RemotiveScraper()
                    for kw in keywords:
                        jobs = await scraper.scrape(role=kw, max_jobs=max_per_source)
                        all_jobs.extend(jobs)

                elif source == "naukri":
                    from scrapers.naukri_scraper import NaukriScraper
                    scraper = NaukriScraper()
                    for kw in keywords:
                        jobs = scraper.scrape(role=kw, location=location, max_jobs=max_per_source)
                        all_jobs.extend(jobs)

                elif source == "indeed":
                    from scrapers.indeed_scraper import IndeedScraper
                    scraper = IndeedScraper()
                    for kw in keywords:
                        jobs = scraper.scrape(role=kw, location=location, max_jobs=max_per_source)
                        all_jobs.extend(jobs)

                elif source == "wellfound":
                    from scrapers.wellfound_scraper import WellfoundScraper
                    scraper = WellfoundScraper()
                    for kw in keywords:
                        jobs = scraper.scrape(role=kw, max_jobs=max_per_source)
                        all_jobs.extend(jobs)

                _scrape_tasks[task_id]["sources_completed"].append(source)
            except Exception as e:
                logger.error(f"Scraper {source} failed: {e}")
                _scrape_tasks[task_id]["errors"].append(f"{source}: {str(e)}")

        _scrape_tasks[task_id]["jobs_found"] = len(all_jobs)

        # Filter and save jobs
        user = db.query(UserProfile).first()
        profile_text = ""
        if user and user.resume_text:
            profile_text = f"{user.skills or ''} {user.target_roles or ''} {user.resume_text[:1000]}"

        added = 0
        duplicates = 0

        for job_data in all_jobs:
            job_url = job_data.get("job_url", "")

            # Duplicate check
            if job_url:
                existing = db.query(Job).filter(Job.job_url == job_url).first()
                if existing:
                    duplicates += 1
                    continue

            # Match score
            match_score = 0.0
            jd_text = job_data.get("jd_text", job_data.get("title", ""))
            if profile_text and jd_text:
                try:
                    match_score = embedder.match_score(profile_text, jd_text[:1000])
                except Exception:
                    pass

            # Filter by minimum match score
            if match_score < settings.MIN_MATCH_SCORE and profile_text:
                continue

            # Save to DB
            job = Job(
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                location=job_data.get("location", ""),
                job_type=job_data.get("job_type", "full-time"),
                source=job_data.get("source", "unknown"),
                job_url=job_url or None,
                jd_text=job_data.get("jd_text", ""),
                match_score=match_score,
            )
            db.add(job)
            added += 1

        db.commit()
        _scrape_tasks[task_id]["jobs_added"] = added
        _scrape_tasks[task_id]["jobs_duplicate"] = duplicates
        _scrape_tasks[task_id]["status"] = "completed"

        # Log scrape run
        run = ScrapeRun(
            source=",".join(sources),
            jobs_found=len(all_jobs),
            jobs_added=added,
            status="success",
            started_at=started_at,
            ended_at=datetime.now(),
        )
        db.add(run)
        db.commit()

    except Exception as e:
        logger.error(f"Background scrape failed: {e}")
        _scrape_tasks[task_id]["status"] = "failed"
        _scrape_tasks[task_id]["errors"].append(str(e))
    finally:
        db.close()
