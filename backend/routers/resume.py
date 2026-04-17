"""Resume generation router."""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.job import Job
from models.application import Application
from models.user_profile import UserProfile
from services.resume_generator import resume_generator
from services.ats_scorer import ats_scorer
from services.cover_letter_service import cover_letter_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate")
async def generate_resume(data: dict, db: Session = Depends(get_db)):
    """Generate a tailored resume for a specific job."""
    job_id = data.get("job_id")
    template = data.get("template", "modern")
    include_cover_letter = data.get("include_cover_letter", False)

    if not job_id:
        raise HTTPException(400, "job_id is required")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")

    user = db.query(UserProfile).first()
    if not user or not user.resume_text:
        raise HTTPException(400, "Upload your master resume first via /api/profile/upload-resume")

    # Build data dicts
    job_data = {
        "title": job.title,
        "company": job.company,
        "jd_text": job.jd_text or "",
        "required_skills": json.loads(job.required_skills) if job.required_skills else [],
        "keywords": json.loads(job.keywords) if job.keywords else [],
    }
    user_data = {
        "full_name": user.full_name,
        "email": user.email or "",
        "phone": user.phone or "",
        "resume_text": user.resume_text,
        "skills": json.loads(user.skills) if user.skills else [],
    }

    # Generate resume
    result = await resume_generator.generate(job_data, user_data, template)

    if not result.get("success"):
        raise HTTPException(500, f"Resume generation failed: {result.get('error')}")

    # Score the generated resume
    score_result = ats_scorer.algorithmic_score(
        resume_text=json.dumps(result.get("resume_data", {})),
        keywords=job_data["keywords"],
        required_skills=job_data["required_skills"],
    )

    # Generate cover letter if requested
    cover_letter_path = None
    if include_cover_letter:
        try:
            cover_text = await cover_letter_service.generate(user_data, job_data)
            # Save cover letter
            from pathlib import Path
            cl_dir = Path(result["resume_pdf_path"]).parent
            cl_path = cl_dir / f"v{result['version']}_cover_letter.txt"
            with open(cl_path, "w", encoding="utf-8") as f:
                f.write(cover_text)
            cover_letter_path = str(cl_path)
        except Exception as e:
            logger.warning(f"Cover letter generation failed: {e}")

    # Create/update application entry
    app = db.query(Application).filter(Application.job_id == job_id).first()
    if app:
        app.ats_score = score_result["total_score"]
        app.resume_pdf_path = result.get("resume_pdf_path")
        app.resume_docx_path = result.get("resume_docx_path")
        app.cover_letter_path = cover_letter_path
        app.resume_version = result.get("version", 1)
        app.tailored_skills = json.dumps(result.get("keywords_used", []))
        app.missing_skills = json.dumps(result.get("missing_skills", []))
    else:
        app = Application(
            job_id=job_id,
            ats_score=score_result["total_score"],
            resume_pdf_path=result.get("resume_pdf_path"),
            resume_docx_path=result.get("resume_docx_path"),
            cover_letter_path=cover_letter_path,
            resume_version=result.get("version", 1),
            tailored_skills=json.dumps(result.get("keywords_used", [])),
            missing_skills=json.dumps(result.get("missing_skills", [])),
        )
        db.add(app)

    db.commit()

    return {
        "success": True,
        "ats_score": score_result["total_score"],
        "resume_pdf_url": f"/api/files/resumes/{job.company.lower().replace(' ', '_')}/v{result['version']}_resume.pdf",
        "resume_docx_url": f"/api/files/resumes/{job.company.lower().replace(' ', '_')}/v{result['version']}_resume.docx",
        "cover_letter_url": f"/api/files/resumes/{job.company.lower().replace(' ', '_')}/v{result['version']}_cover_letter.txt" if cover_letter_path else None,
        "missing_skills": result.get("missing_skills", []),
        "tailored_summary": result.get("tailored_summary", ""),
        "keywords_added": result.get("keywords_used", []),
    }


@router.get("/score/{job_id}")
async def get_resume_score(job_id: int, db: Session = Depends(get_db)):
    """Get ATS score breakdown for a job's resume."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")

    app = db.query(Application).filter(Application.job_id == job_id).first()
    if not app:
        raise HTTPException(404, "No resume generated for this job yet")

    # Re-score with full detail
    keywords = json.loads(job.keywords) if job.keywords else []
    required_skills = json.loads(job.required_skills) if job.required_skills else []
    resume_text = json.dumps(app.tailored_skills or "")

    score = ats_scorer.algorithmic_score(resume_text, keywords, required_skills)

    return {
        "ats_score": score["total_score"],
        "breakdown": {
            "keyword_match": score["keyword_match"],
            "skills_coverage": score["skills_coverage"],
            "format_compliance": score["format_compliance"],
            "experience_match": score["experience_match"],
        },
        "matched_keywords": score["matched_keywords"],
        "missing_keywords": score["missing_keywords"],
        "matched_skills": score["matched_skills"],
        "missing_skills": score["missing_skills"],
    }
