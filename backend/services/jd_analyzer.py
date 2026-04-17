"""Job description analyzer — extracts structured data from JDs using Gemini."""

import json
import logging
from services.gemini_service import llm
from services.prompt_templates import JD_ANALYSIS_SYSTEM, jd_analysis_user

logger = logging.getLogger(__name__)


class JDAnalyzer:
    """Analyze job descriptions and extract structured information."""

    async def analyze(self, jd_text: str) -> dict:
        """Analyze a job description and return structured data."""
        try:
            result = await llm.generate_json(
                JD_ANALYSIS_SYSTEM,
                jd_analysis_user(jd_text)
            )
            return result
        except Exception as e:
            logger.error(f"JD analysis failed: {e}")
            # Return a basic fallback
            return self._basic_analysis(jd_text)

    def _basic_analysis(self, jd_text: str) -> dict:
        """Fallback: basic keyword extraction without LLM."""
        import re
        text_lower = jd_text.lower()

        # Common tech skills to look for
        all_skills = [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
            "Spring Boot", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "Git", "CI/CD", "Linux", "REST API", "GraphQL", "Microservices",
            "Machine Learning", "TensorFlow", "PyTorch", "SQL",
        ]

        found_skills = [s for s in all_skills if s.lower() in text_lower]

        # Try to extract experience
        exp_match = re.search(r"(\d+)\+?\s*[-–to]\s*(\d+)\s*years?", jd_text, re.IGNORECASE)
        min_exp = float(exp_match.group(1)) if exp_match else 0
        max_exp = float(exp_match.group(2)) if exp_match else 0

        return {
            "required_skills": found_skills[:10],
            "nice_to_have_skills": found_skills[10:],
            "min_exp_years": min_exp,
            "max_exp_years": max_exp,
            "seniority": "mid",
            "job_type": "full-time",
            "work_mode": "unknown",
            "top_keywords": found_skills[:5],
            "responsibilities": [],
            "company_culture_hints": [],
            "salary_mentioned": "",
            "education_required": "",
        }


jd_analyzer = JDAnalyzer()
