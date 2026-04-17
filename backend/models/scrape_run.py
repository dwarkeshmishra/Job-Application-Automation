"""Scrape run audit log ORM model."""

from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String)           # "linkedin" | "naukri" | "scheduler"
    jobs_found = Column(Integer)
    jobs_added = Column(Integer)
    status = Column(String)           # "success" | "failed" | "partial"
    error_msg = Column(Text)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)

    def __repr__(self):
        return f"<ScrapeRun(id={self.id}, source='{self.source}', status='{self.status}')>"
