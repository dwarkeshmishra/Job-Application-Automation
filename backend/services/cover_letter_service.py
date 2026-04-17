"""Cover letter generation service using Gemini AI."""

import logging
from services.gemini_service import llm
from services.prompt_templates import COVER_LETTER_SYSTEM, cover_letter_user

logger = logging.getLogger(__name__)


class CoverLetterService:
    """Generate tailored cover letters."""

    async def generate(self, user_data: dict, job_data: dict) -> str:
        """Generate a cover letter for a specific job application."""
        try:
            full_name = user_data.get("full_name", "Candidate")
            job_title = job_data.get("title", "Software Engineer")
            company = job_data.get("company", "Company")
            skills = user_data.get("skills", [])
            if isinstance(skills, str):
                import json
                skills = json.loads(skills)

            top_skills = skills[:5] if skills else ["Python"]

            # Get best achievement from resume text
            resume_text = user_data.get("resume_text", "")
            top_achievement = self._extract_top_achievement(resume_text)

            jd_text = job_data.get("jd_text", "")
            jd_summary = jd_text[:500] if len(jd_text) > 500 else jd_text

            result = await llm.generate(
                COVER_LETTER_SYSTEM,
                cover_letter_user(
                    full_name=full_name,
                    job_title=job_title,
                    company_name=company,
                    top_skills=top_skills,
                    top_achievement=top_achievement,
                    jd_summary=jd_summary,
                )
            )
            return result.strip()

        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            return f"Error generating cover letter: {str(e)}"

    def _extract_top_achievement(self, resume_text: str) -> str:
        """Extract the most impressive achievement bullet from resume text."""
        import re
        lines = resume_text.split("\n")
        best = ""
        best_score = 0

        for line in lines:
            line = line.strip()
            if len(line) < 20:
                continue
            # Score based on having numbers, percentages, action verbs
            score = 0
            if re.search(r"\d+%", line):
                score += 3
            if re.search(r"\d+x", line, re.IGNORECASE):
                score += 3
            if re.search(r"\d+", line):
                score += 1
            action_verbs = ["built", "developed", "led", "reduced", "increased",
                          "architected", "deployed", "optimized", "improved"]
            if any(v in line.lower() for v in action_verbs):
                score += 2
            if score > best_score:
                best_score = score
                best = line

        return best or "Delivered high-impact software projects"


cover_letter_service = CoverLetterService()
