"""JD Analysis router."""

import logging
from fastapi import APIRouter, HTTPException
from services.jd_analyzer import jd_analyzer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/jd")
async def analyze_jd(data: dict):
    """Analyze a job description and extract structured information."""
    jd_text = data.get("jd_text", "")
    if not jd_text:
        raise HTTPException(400, "jd_text is required")

    result = await jd_analyzer.analyze(jd_text)
    return result
