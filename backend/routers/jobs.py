"""Jobs router — list jobs, add manual job, get single job."""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models.job import Job
from models.application import Application
from models.user_profile import UserProfile
from services.embedding_service import embedder
from services.jd_analyzer import jd_analyzer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def list_jobs(
    status: str = None,
    min_score: int = None,
    source: str = None,
    search: str = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List all scraped jobs with filters."""
    query = db.query(Job).filter(Job.is_active == True)

    if source:
        query = query.filter(Job.source == source)
    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.company.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    jobs = query.order_by(Job.scraped_at.desc()).offset(offset).limit(limit).all()

    result = []
    for job in jobs:
        # Get application status if exists
        app = db.query(Application).filter(Application.job_id == job.id).first()
        app_status = app.status if app else "not_applied"
        ats_score = app.ats_score if app else None

        if status and app_status != status:
            continue
        if min_score and ats_score and ats_score < min_score:
            continue

        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "source": job.source,
            "job_url": job.job_url,
            "match_score": job.match_score,
            "ats_score": ats_score,
            "status": app_status,
            "required_skills": json.loads(job.required_skills) if job.required_skills else [],
            "scraped_at": str(job.scraped_at) if job.scraped_at else None,
        })

    return {"total": total, "jobs": result}


@router.get("/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job with full details."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "job_type": job.job_type,
        "source": job.source,
        "job_url": job.job_url,
        "jd_text": job.jd_text,
        "match_score": job.match_score,
        "required_skills": json.loads(job.required_skills) if job.required_skills else [],
        "nice_to_have": json.loads(job.nice_to_have) if job.nice_to_have else [],
        "keywords": json.loads(job.keywords) if job.keywords else [],
        "min_exp_years": job.min_exp_years,
        "max_exp_years": job.max_exp_years,
        "salary_range": job.salary_range,
        "scraped_at": str(job.scraped_at) if job.scraped_at else None,
    }


@router.post("/manual")
async def add_manual_job(data: dict, db: Session = Depends(get_db)):
    """Add a job manually by pasting job description."""
    title = data.get("title", "")
    company = data.get("company", "")
    job_url = data.get("job_url", "")
    jd_text = data.get("jd_text", "")

    if not title or not company:
        raise HTTPException(400, "Title and company are required")

    # Check for duplicate
    if job_url:
        existing = db.query(Job).filter(Job.job_url == job_url).first()
        if existing:
            return {"job_id": existing.id, "message": "Job already exists", "duplicate": True}

    # Analyze JD
    analysis = {}
    try:
        analysis = await jd_analyzer.analyze(jd_text)
    except Exception as e:
        logger.warning(f"JD analysis failed: {e}")

    # Calculate match score
    match_score = 0.0
    try:
        user = db.query(UserProfile).first()
        if user and user.resume_text:
            profile_text = f"{user.skills or ''} {user.target_roles or ''} {user.resume_text[:1000]}"
            match_score = embedder.match_score(profile_text, jd_text[:1000])
    except Exception as e:
        logger.warning(f"Match score calculation failed: {e}")

    # Generate embedding
    try:
        embedding = embedder.embed(jd_text[:1000])
    except Exception:
        embedding = []

    job = Job(
        title=title,
        company=company,
        location=data.get("location", analysis.get("work_mode", "")),
        job_type=analysis.get("job_type", "full-time"),
        source=data.get("source", "manual"),
        job_url=job_url or None,
        jd_text=jd_text,
        jd_embedding=json.dumps(embedding),
        keywords=json.dumps(analysis.get("top_keywords", [])),
        required_skills=json.dumps(analysis.get("required_skills", [])),
        nice_to_have=json.dumps(analysis.get("nice_to_have_skills", [])),
        min_exp_years=analysis.get("min_exp_years"),
        max_exp_years=analysis.get("max_exp_years"),
        salary_range=analysis.get("salary_mentioned", ""),
        match_score=match_score,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "match_score": round(match_score, 2),
        "keywords": analysis.get("top_keywords", []),
        "required_skills": analysis.get("required_skills", []),
        "message": "Job added. Ready to generate resume.",
    }


@router.delete("/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    db.delete(job)
    db.commit()
    return {"success": True, "message": f"Job {job_id} deleted"}
