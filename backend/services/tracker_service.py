"""Tracker service — CRUD operations for job applications."""

import json
import logging
from datetime import datetime, date
from sqlalchemy.orm import Session
from models.application import Application
from models.job import Job

logger = logging.getLogger(__name__)


class TrackerService:
    """Manage job application tracking."""

    def get_all(self, db: Session, status: str = None) -> dict:
        """Get all applications with summary stats."""
        query = db.query(Application).join(Job)

        if status:
            query = query.filter(Application.status == status)

        applications = query.order_by(Application.date_added.desc()).all()

        # Summary counts
        all_apps = db.query(Application).all()
        summary = {
            "total": len(all_apps),
            "not_applied": sum(1 for a in all_apps if a.status == "not_applied"),
            "applied": sum(1 for a in all_apps if a.status == "applied"),
            "interview": sum(1 for a in all_apps if a.status in ("interview_r1", "interview_r2")),
            "offer": sum(1 for a in all_apps if a.status == "offer"),
            "rejected": sum(1 for a in all_apps if a.status == "rejected"),
        }

        app_list = []
        for app in applications:
            job = app.job
            app_list.append({
                "id": app.id,
                "job_id": app.job_id,
                "company": job.company if job else "Unknown",
                "role": job.title if job else "Unknown",
                "location": job.location if job else "",
                "source": job.source if job else "",
                "job_url": job.job_url if job else "",
                "ats_score": app.ats_score,
                "match_score": job.match_score if job else 0,
                "status": app.status,
                "applied_date": str(app.applied_date) if app.applied_date else None,
                "interview_date": str(app.interview_date) if app.interview_date else None,
                "notes": app.notes,
                "resume_pdf_path": app.resume_pdf_path,
                "resume_docx_path": app.resume_docx_path,
                "cover_letter_path": app.cover_letter_path,
                "missing_skills": json.loads(app.missing_skills) if app.missing_skills else [],
                "date_added": str(app.date_added) if app.date_added else None,
            })

        return {"summary": summary, "applications": app_list}

    def create(self, db: Session, job_id: int, ats_score: int = None,
               resume_pdf_path: str = None, resume_docx_path: str = None,
               cover_letter_path: str = None, tailored_skills: list = None,
               missing_skills: list = None) -> Application:
        """Create a new application entry."""
        app = Application(
            job_id=job_id,
            ats_score=ats_score,
            resume_pdf_path=resume_pdf_path,
            resume_docx_path=resume_docx_path,
            cover_letter_path=cover_letter_path,
            tailored_skills=json.dumps(tailored_skills) if tailored_skills else None,
            missing_skills=json.dumps(missing_skills) if missing_skills else None,
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        logger.info(f"Application created: id={app.id}, job_id={job_id}")
        return app

    def update(self, db: Session, application_id: int, **kwargs) -> Application:
        """Update an application's fields."""
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            raise ValueError(f"Application {application_id} not found")

        updated_fields = []
        for field, value in kwargs.items():
            if hasattr(app, field) and value is not None:
                if field in ("tailored_skills", "missing_skills") and isinstance(value, list):
                    value = json.dumps(value)
                if field == "applied_date" and isinstance(value, str):
                    value = date.fromisoformat(value)
                if field == "interview_date" and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                setattr(app, field, value)
                updated_fields.append(field)

        db.commit()
        db.refresh(app)
        logger.info(f"Application {application_id} updated: {updated_fields}")
        return app

    def delete(self, db: Session, application_id: int) -> bool:
        """Delete an application."""
        app = db.query(Application).filter(Application.id == application_id).first()
        if app:
            db.delete(app)
            db.commit()
            return True
        return False


tracker_service = TrackerService()
