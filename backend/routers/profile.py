"""Profile router — upload master resume, get/update profile."""

import json
import shutil
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user_profile import UserProfile
from services.resume_parser import resume_parser
from services.embedding_service import embedder
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload master resume PDF or DOCX."""
    if not file.filename.lower().endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(400, "Only PDF and DOCX files are supported")

    # Save file
    upload_dir = settings.data_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"master_resume{file.filename[file.filename.rfind('.'):]}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Parse resume
    extracted_text = resume_parser.parse(str(file_path))
    detected_skills = resume_parser.detect_skills(extracted_text)
    years_exp = resume_parser.estimate_experience_years(extracted_text)

    # Generate embedding
    try:
        embedding = embedder.embed(extracted_text[:2000])
    except Exception:
        embedding = []

    # Update or create profile
    profile = db.query(UserProfile).first()
    if profile:
        profile.resume_path = str(file_path)
        profile.resume_text = extracted_text
        profile.skills = json.dumps(detected_skills)
        profile.years_exp = years_exp
        profile.resume_embedding = json.dumps(embedding)
    else:
        profile = UserProfile(
            full_name="User",
            resume_path=str(file_path),
            resume_text=extracted_text,
            skills=json.dumps(detected_skills),
            years_exp=years_exp,
            resume_embedding=json.dumps(embedding),
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)

    return {
        "success": True,
        "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
        "skills_detected": detected_skills,
        "years_experience": years_exp,
        "resume_path": str(file_path),
    }


@router.get("")
async def get_profile(db: Session = Depends(get_db)):
    """Get current user profile."""
    profile = db.query(UserProfile).first()
    if not profile:
        return {"message": "No profile found. Upload your resume first."}

    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "email": profile.email,
        "phone": profile.phone,
        "location": profile.location,
        "linkedin_url": profile.linkedin_url,
        "github_url": profile.github_url,
        "skills": json.loads(profile.skills) if profile.skills else [],
        "target_roles": json.loads(profile.target_roles) if profile.target_roles else [],
        "target_locations": json.loads(profile.target_locations) if profile.target_locations else [],
        "years_exp": profile.years_exp,
        "resume_path": profile.resume_path,
    }


@router.put("")
async def update_profile(data: dict, db: Session = Depends(get_db)):
    """Update profile fields."""
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile(full_name=data.get("full_name", "User"))
        db.add(profile)

    field_map = {
        "full_name": "full_name", "email": "email", "phone": "phone",
        "location": "location", "linkedin_url": "linkedin_url",
        "github_url": "github_url", "years_exp": "years_exp",
    }

    for key, attr in field_map.items():
        if key in data:
            setattr(profile, attr, data[key])

    # JSON fields
    for key in ("skills", "target_roles", "target_locations"):
        if key in data:
            val = data[key]
            setattr(profile, key, json.dumps(val) if isinstance(val, list) else val)

    db.commit()
    db.refresh(profile)
    return {"success": True, "profile_id": profile.id}
