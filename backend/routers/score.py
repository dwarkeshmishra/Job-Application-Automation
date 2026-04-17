"""ATS scoring router."""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.job import Job
from models.user_profile import UserProfile
from services.ats_scorer import ats_scorer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ats")
async def score_resume(data: dict, db: Session = Depends(get_db)):
    """Score a resume against a job description."""
    job_id = data.get("job_id")
    resume_text = data.get("resume_text")
    jd_text = data.get("jd_text")

    # If job_id provided, fetch JD from database
    if job_id:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(404, "Job not found")
        jd_text = job.jd_text
        keywords = json.loads(job.keywords) if job.keywords else []
        required_skills = json.loads(job.required_skills) if job.required_skills else []
    else:
        keywords = data.get("keywords", [])
        required_skills = data.get("required_skills", [])

    # If no resume text provided, use master resume
    if not resume_text:
        user = db.query(UserProfile).first()
        if user and user.resume_text:
            resume_text = user.resume_text
        else:
            raise HTTPException(400, "No resume text provided and no master resume uploaded")

    if not jd_text:
        raise HTTPException(400, "Job description text is required")

    # Use LLM-enhanced scoring if requested
    use_llm = data.get("use_llm", False)

    if use_llm:
        result = await ats_scorer.full_score(resume_text, jd_text, keywords, required_skills)
    else:
        result = ats_scorer.algorithmic_score(resume_text, keywords, required_skills)

    return result
