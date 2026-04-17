"""Excel export router."""

import logging
from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from services.excel_exporter import excel_exporter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/excel")
async def export_excel(db: Session = Depends(get_db)):
    """Export job tracker as Excel file."""
    file_path = excel_exporter.export(db)
    path = Path(file_path)

    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(500, "Export file not created")

    return FileResponse(
        path=str(path),
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
