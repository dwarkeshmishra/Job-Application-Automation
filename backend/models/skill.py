"""Skills library ORM model."""

from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class SkillLibrary(Base):
    __tablename__ = "skills_library"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String, unique=True, nullable=False)
    category = Column(String)       # "language", "framework", "cloud", "database", "tool"
    frequency = Column(Integer, default=0)   # How many JDs mention this skill
    user_has = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Skill(name='{self.skill_name}', freq={self.frequency})>"
