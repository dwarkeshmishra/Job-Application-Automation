"""User profile ORM model."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from database import Base


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    location = Column(String)
    linkedin_url = Column(String)
    github_url = Column(String)
    target_roles = Column(Text)       # JSON: ["Software Engineer", "Backend Dev"]
    target_locations = Column(Text)    # JSON: ["Bangalore", "Remote"]
    skills = Column(Text)             # JSON: ["Python", "React", "SQL"]
    years_exp = Column(Float)
    resume_path = Column(String)       # Path to master resume PDF
    resume_text = Column(Text)         # Extracted plain text of master resume
    resume_embedding = Column(Text)    # JSON: 384-dim vector
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserProfile(id={self.id}, name='{self.full_name}')>"
