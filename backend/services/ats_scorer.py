"""ATS scorer — hybrid algorithmic + LLM scoring."""

import re
import logging
from services.gemini_service import llm
from services.prompt_templates import ATS_SCORE_SYSTEM, ats_score_user

logger = logging.getLogger(__name__)


class ATSScorer:
    """Score resumes against job descriptions."""

    def algorithmic_score(self, resume_text: str,
                          keywords: list, required_skills: list) -> dict:
        """Fast deterministic score — no LLM call."""
        resume_lower = resume_text.lower()

        # 1. Keyword match (0-40)
        matched_kw = [k for k in keywords if k.lower() in resume_lower]
        kw_score = min(40, int((len(matched_kw) / max(len(keywords), 1)) * 40))

        # 2. Skills coverage (0-35)
        matched_sk = [s for s in required_skills if s.lower() in resume_lower]
        sk_score = min(35, int((len(matched_sk) / max(len(required_skills), 1)) * 35))

        # 3. Format compliance (0-15)
        sections = ["experience", "education", "skills", "projects"]
        found_sections = sum(1 for s in sections if s in resume_lower)
        has_email = bool(re.search(r"[\w.-]+@[\w.-]+\.\w+", resume_text))
        has_phone = bool(re.search(r"[+\d][\d\s\-()]{8,}", resume_text))
        fmt_score = (found_sections * 3) + (has_email * 2) + (has_phone * 1)
        fmt_score = min(15, fmt_score)

        # 4. Experience match — basic check (0-10)
        exp_score = 8  # Default, LLM call gives precise score

        total = kw_score + sk_score + fmt_score + exp_score
        return {
            "total_score": total,
            "keyword_match": kw_score,
            "skills_coverage": sk_score,
            "format_compliance": fmt_score,
            "experience_match": exp_score,
            "matched_keywords": matched_kw,
            "missing_keywords": [k for k in keywords if k.lower() not in resume_lower],
            "matched_skills": matched_sk,
            "missing_skills": [s for s in required_skills if s.lower() not in resume_lower],
        }

    async def llm_score(self, resume_text: str, jd_text: str) -> dict:
        """Slower but precise — includes recommendations from Gemini."""
        try:
            return await llm.generate_json(
                ATS_SCORE_SYSTEM,
                ats_score_user(jd_text, resume_text)
            )
        except Exception as e:
            logger.error(f"LLM ATS scoring failed: {e}")
            # Fallback to algorithmic
            return self.algorithmic_score(resume_text, [], [])

    async def full_score(self, resume_text: str, jd_text: str,
                         keywords: list, required_skills: list) -> dict:
        """Combined score: algorithmic base + LLM recommendations."""
        algo = self.algorithmic_score(resume_text, keywords, required_skills)

        try:
            llm_result = await self.llm_score(resume_text, jd_text)
            # Merge: use algorithmic scores but LLM recommendations
            algo["recommendations"] = llm_result.get("recommendations", [])
            algo["format_issues"] = llm_result.get("format_issues", [])
        except Exception:
            algo["recommendations"] = []
            algo["format_issues"] = []

        return algo


ats_scorer = ATSScorer()
