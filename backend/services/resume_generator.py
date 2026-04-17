"""Resume generator — creates tailored resumes using Gemini AI."""

import json
import logging
from pathlib import Path
from services.gemini_service import llm
from services.prompt_templates import RESUME_SYSTEM, resume_user_prompt
from services.file_builder import file_builder
from config import settings

logger = logging.getLogger(__name__)


class ResumeGenerator:
    """Generate tailored resumes for specific job descriptions."""

    async def generate(self, job_data: dict, user_data: dict,
                       template: str = "modern") -> dict:
        """
        Generate a tailored resume for a specific job.

        Args:
            job_data: dict with title, company, jd_text, required_skills, keywords
            user_data: dict with full_name, resume_text, skills
            template: "modern" | "classic" | "minimal"

        Returns:
            dict with paths, ats_score, missing_skills, etc.
        """
        try:
            # Extract info
            job_title = job_data.get("title", "Software Engineer")
            company = job_data.get("company", "Company")
            jd_text = job_data.get("jd_text", "")
            required_skills = job_data.get("required_skills", [])
            keywords = job_data.get("keywords", [])

            if isinstance(required_skills, str):
                required_skills = json.loads(required_skills)
            if isinstance(keywords, str):
                keywords = json.loads(keywords)

            master_resume = user_data.get("resume_text", "")

            # Generate tailored resume via Gemini
            prompt = resume_user_prompt(
                job_description=jd_text,
                master_resume_text=master_resume,
                job_title=job_title,
                company_name=company,
                required_skills=required_skills,
                keywords=keywords,
            )

            resume_data = await llm.generate_json(RESUME_SYSTEM, prompt)
            logger.info(f"Resume generated for {job_title} at {company}")

            # Build output files
            company_slug = company.lower().replace(" ", "_").replace(".", "")
            output_dir = settings.data_path / "resumes" / company_slug
            output_dir.mkdir(parents=True, exist_ok=True)

            # Determine version number
            existing = list(output_dir.glob("v*_resume.pdf"))
            version = len(existing) + 1

            # Build PDF and DOCX
            full_name = user_data.get("full_name", "Candidate")
            email = user_data.get("email", "")
            phone = user_data.get("phone", "")

            pdf_path = file_builder.build_pdf(
                resume_data=resume_data,
                output_dir=str(output_dir),
                version=version,
                template=template,
                contact_info={"name": full_name, "email": email, "phone": phone},
            )

            docx_path = file_builder.build_docx(
                resume_data=resume_data,
                output_dir=str(output_dir),
                version=version,
                contact_info={"name": full_name, "email": email, "phone": phone},
            )

            return {
                "success": True,
                "resume_data": resume_data,
                "resume_pdf_path": pdf_path,
                "resume_docx_path": docx_path,
                "version": version,
                "tailored_summary": resume_data.get("summary", ""),
                "keywords_used": resume_data.get("keywords_used", []),
                "missing_skills": [
                    s for s in required_skills
                    if s.lower() not in json.dumps(resume_data).lower()
                ],
            }

        except Exception as e:
            logger.error(f"Resume generation failed: {e}")
            return {"success": False, "error": str(e)}


resume_generator = ResumeGenerator()
