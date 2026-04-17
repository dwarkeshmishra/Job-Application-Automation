"""Application tracker router."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.tracker_service import tracker_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def get_tracker(status: str = None, db: Session = Depends(get_db)):
    """Get all tracked applications with summary stats."""
    return tracker_service.get_all(db, status=status)


@router.patch("/{application_id}")
async def update_application(application_id: int, data: dict,
                              db: Session = Depends(get_db)):
    """Update application status, notes, dates, etc."""
    try:
        app = tracker_service.update(db, application_id, **data)
        updated_fields = [k for k in data.keys() if data[k] is not None]
        return {
            "success": True,
            "application_id": app.id,
            "updated_fields": updated_fields,
        }
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{application_id}")
async def delete_application(application_id: int, db: Session = Depends(get_db)):
    """Delete an application."""
    success = tracker_service.delete(db, application_id)
    if not success:
        raise HTTPException(404, "Application not found")
    return {"success": True, "message": f"Application {application_id} deleted"}
