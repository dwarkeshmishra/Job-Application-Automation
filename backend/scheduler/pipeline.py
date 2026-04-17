"""Nightly scheduler pipeline — APScheduler cron job."""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler = None


async def nightly_pipeline():
    """Full pipeline: scrape → filter → generate resumes → export."""
    from database import SessionLocal
    from models.user_profile import UserProfile
    from services.embedding_service import embedder
    from services.excel_exporter import excel_exporter

    logger.info("=== NIGHTLY PIPELINE STARTED ===")
    db = SessionLocal()

    try:
        user = db.query(UserProfile).first()
        if not user:
            logger.warning("No user profile found. Skipping pipeline.")
            return

        # 1. Scrape new jobs from available sources
        all_jobs = []

        try:
            from scrapers.remotive_scraper import RemotiveScraper
            scraper = RemotiveScraper()

            # Get target roles from user profile
            import json
            target_roles = json.loads(user.target_roles) if user.target_roles else ["software engineer"]

            for role in target_roles[:3]:  # Limit to 3 roles
                jobs = await scraper.scrape(role=role, max_jobs=25)
                all_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"Remotive scrape failed: {e}")

        try:
            from scrapers.naukri_scraper import NaukriScraper
            naukri = NaukriScraper()
            target_roles_list = json.loads(user.target_roles) if user.target_roles else ["software engineer"]
            for role in target_roles_list[:2]:
                jobs = naukri.scrape(role=role, max_jobs=15)
                all_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"Naukri scrape failed: {e}")

        logger.info(f"Scraped {len(all_jobs)} raw jobs")

        # 2. Filter by semantic match score
        profile_text = f"{user.skills or ''} {user.target_roles or ''} {(user.resume_text or '')[:1000]}"
        from models.job import Job

        new_count = 0
        for job_data in all_jobs:
            # Duplicate check
            job_url = job_data.get("job_url", "")
            if job_url:
                existing = db.query(Job).filter(Job.job_url == job_url).first()
                if existing:
                    continue

            jd_text = job_data.get("jd_text", job_data.get("title", ""))
            match_score = 0.0
            try:
                if profile_text and jd_text:
                    match_score = embedder.match_score(profile_text, jd_text[:1000])
            except Exception:
                pass

            if match_score >= 0.62:
                job = Job(
                    title=job_data.get("title", ""),
                    company=job_data.get("company", ""),
                    location=job_data.get("location", ""),
                    source=job_data.get("source", ""),
                    job_url=job_url or None,
                    jd_text=jd_text,
                    match_score=match_score,
                )
                db.add(job)
                new_count += 1

        db.commit()
        logger.info(f"Added {new_count} new relevant jobs")

        # 3. Export Excel tracker
        try:
            excel_exporter.export(db)
            logger.info("Excel tracker exported")
        except Exception as e:
            logger.error(f"Excel export failed: {e}")

        logger.info("=== NIGHTLY PIPELINE COMPLETE ===")

    except Exception as e:
        logger.error(f"Nightly pipeline failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the APScheduler with nightly pipeline."""
    global _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        nightly_pipeline,
        CronTrigger(hour=2, minute=0),  # 2:00 AM every night
        id="nightly_pipeline",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started — nightly job at 2:00 AM")
