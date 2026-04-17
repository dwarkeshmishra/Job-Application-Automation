"""Application (job tracker) ORM model."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String, default="not_applied")
    # Status values: not_applied | applied | interview_r1 |
    # interview_r2 | offer | rejected | withdrawn
    ats_score = Column(Integer)              # 0-100
    resume_pdf_path = Column(String)
    resume_docx_path = Column(String)
    cover_letter_path = Column(String)
    resume_version = Column(Integer, default=1)
    tailored_skills = Column(Text)           # JSON: skills highlighted for this job
    missing_skills = Column(Text)            # JSON: skills gap
    notes = Column(Text)
    applied_date = Column(Date)
    interview_date = Column(DateTime)
    recruiter_name = Column(String)
    recruiter_email = Column(String)
    referral_email_path = Column(String)
    date_added = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    job = relationship("Job", backref="applications")

    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, status='{self.status}')>"
