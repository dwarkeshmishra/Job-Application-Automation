"""Resume parser — extracts text from PDF and DOCX files."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ResumeParser:
    """Extract text content from PDF and DOCX resume files."""

    def parse(self, file_path: str) -> str:
        """Parse a resume file and return plain text."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return self._parse_pdf(path)
        elif ext in (".docx", ".doc"):
            return self._parse_docx(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _parse_pdf(self, path: Path) -> str:
        """Extract text from PDF using PyMuPDF."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"PDF parse error: {e}")
            raise

    def _parse_docx(self, path: Path) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document
            doc = Document(str(path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs).strip()
        except Exception as e:
            logger.error(f"DOCX parse error: {e}")
            raise

    def detect_skills(self, text: str, known_skills: list[str] | None = None) -> list[str]:
        """Detect skills from resume text using keyword matching."""
        if known_skills is None:
            known_skills = [
                "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
                "React", "Angular", "Vue", "Next.js", "Node.js", "Express", "Django",
                "Flask", "FastAPI", "Spring Boot", "Ruby on Rails",
                "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Elasticsearch",
                "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
                "Git", "CI/CD", "Jenkins", "GitHub Actions", "Linux",
                "REST API", "GraphQL", "gRPC", "Microservices",
                "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
                "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
                "HTML", "CSS", "Tailwind", "Bootstrap", "SASS",
                "Agile", "Scrum", "Jira", "Figma", "Firebase",
            ]

        text_lower = text.lower()
        found = [s for s in known_skills if s.lower() in text_lower]
        return sorted(set(found))

    def estimate_experience_years(self, text: str) -> float:
        """Rough estimate of years of experience from resume text."""
        import re
        # Look for patterns like "X years" or "X+ years"
        patterns = [
            r"(\d+\.?\d*)\+?\s*years?\s*(?:of\s+)?(?:experience|exp)",
            r"(\d+\.?\d*)\+?\s*yrs?\s*(?:of\s+)?(?:experience|exp)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))

        # Count date ranges in experience sections
        date_ranges = re.findall(
            r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current)",
            text, re.IGNORECASE
        )
        if date_ranges:
            total = 0
            for start, end in date_ranges:
                start_year = int(start)
                end_year = 2025 if end.lower() in ("present", "current") else int(end)
                total += max(0, end_year - start_year)
            return float(total)

        return 0.0


resume_parser = ResumeParser()
