"""Job listing ORM model."""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    job_type = Column(String)          # "full-time", "contract", "remote"
    source = Column(String)            # "linkedin", "naukri", "indeed", "manual"
    job_url = Column(String, unique=True)
    jd_text = Column(Text)             # Full job description raw text
    jd_embedding = Column(Text)        # JSON: 384-dim vector
    keywords = Column(Text)            # JSON: extracted keywords
    required_skills = Column(Text)     # JSON: ["Python", "AWS", "Docker"]
    nice_to_have = Column(Text)        # JSON: optional skills
    min_exp_years = Column(Float)
    max_exp_years = Column(Float)
    salary_range = Column(String)
    match_score = Column(Float)        # 0.0-1.0 cosine similarity
    scraped_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"
