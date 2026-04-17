"""File builder — generates PDF and DOCX resume files."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileBuilder:
    """Build PDF and DOCX files from structured resume data."""

    def build_pdf(self, resume_data: dict, output_dir: str, version: int,
                  template: str = "modern", contact_info: dict = None) -> str:
        """Generate a PDF resume from structured data using WeasyPrint."""
        output_path = Path(output_dir) / f"v{version}_resume.pdf"

        try:
            html_content = self._render_html(resume_data, template, contact_info)
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(str(output_path))
            logger.info(f"PDF resume saved: {output_path}")
        except ImportError:
            logger.warning("WeasyPrint not available, creating plain text PDF fallback")
            self._write_text_fallback(resume_data, str(output_path), contact_info)
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            self._write_text_fallback(resume_data, str(output_path), contact_info)

        return str(output_path)

    def build_docx(self, resume_data: dict, output_dir: str, version: int,
                   contact_info: dict = None) -> str:
        """Generate a DOCX resume from structured data."""
        output_path = Path(output_dir) / f"v{version}_resume.docx"

        try:
            from docx import Document
            from docx.shared import Pt, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            doc = Document()

            # Style defaults
            style = doc.styles["Normal"]
            font = style.font
            font.name = "Calibri"
            font.size = Pt(11)

            # Header — Name & Contact
            name = contact_info.get("name", "Candidate") if contact_info else "Candidate"
            heading = doc.add_heading(name, level=0)
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

            if contact_info:
                contact_parts = []
                if contact_info.get("email"):
                    contact_parts.append(contact_info["email"])
                if contact_info.get("phone"):
                    contact_parts.append(contact_info["phone"])
                if contact_parts:
                    p = doc.add_paragraph(" | ".join(contact_parts))
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Summary
            if resume_data.get("summary"):
                doc.add_heading("Professional Summary", level=1)
                doc.add_paragraph(resume_data["summary"])

            # Skills
            skills = resume_data.get("skills", {})
            if skills:
                doc.add_heading("Technical Skills", level=1)
                for category, skill_list in skills.items():
                    if skill_list:
                        cat_name = category.replace("_", " ").title()
                        doc.add_paragraph(
                            f"{cat_name}: {', '.join(skill_list)}",
                            style="List Bullet"
                        )

            # Experience
            experience = resume_data.get("experience", [])
            if experience:
                doc.add_heading("Experience", level=1)
                for exp in experience:
                    p = doc.add_paragraph()
                    run = p.add_run(f"{exp.get('role', '')} — {exp.get('company', '')}")
                    run.bold = True
                    p.add_run(f"\n{exp.get('duration', '')}")
                    for bullet in exp.get("bullets", []):
                        doc.add_paragraph(bullet, style="List Bullet")

            # Projects
            projects = resume_data.get("projects", [])
            if projects:
                doc.add_heading("Projects", level=1)
                for proj in projects:
                    p = doc.add_paragraph()
                    run = p.add_run(proj.get("name", ""))
                    run.bold = True
                    tech = proj.get("tech_stack", "")
                    if tech:
                        p.add_run(f" | {tech}")
                    for bullet in proj.get("bullets", []):
                        doc.add_paragraph(bullet, style="List Bullet")

            # Education
            education = resume_data.get("education", [])
            if education:
                doc.add_heading("Education", level=1)
                for edu in education:
                    p = doc.add_paragraph()
                    run = p.add_run(f"{edu.get('degree', '')} — {edu.get('institution', '')}")
                    run.bold = True
                    details = []
                    if edu.get("year"):
                        details.append(edu["year"])
                    if edu.get("cgpa"):
                        details.append(f"CGPA: {edu['cgpa']}")
                    if details:
                        p.add_run(f"\n{' | '.join(details)}")

            # Certifications
            certs = resume_data.get("certifications", [])
            if certs:
                doc.add_heading("Certifications", level=1)
                for cert in certs:
                    doc.add_paragraph(cert, style="List Bullet")

            doc.save(str(output_path))
            logger.info(f"DOCX resume saved: {output_path}")

        except Exception as e:
            logger.error(f"DOCX generation failed: {e}")
            # Create a minimal text file as fallback
            output_path = Path(output_dir) / f"v{version}_resume.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(str(resume_data))

        return str(output_path)

    def _render_html(self, resume_data: dict, template: str,
                     contact_info: dict = None) -> str:
        """Render resume data as HTML for PDF conversion."""
        name = contact_info.get("name", "Candidate") if contact_info else "Candidate"
        email = contact_info.get("email", "") if contact_info else ""
        phone = contact_info.get("phone", "") if contact_info else ""

        # Load template file
        template_path = Path(__file__).parent.parent / "templates" / f"resume_{template}.html"
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                html_template = f.read()
            # Simple placeholder replacement
            html_template = html_template.replace("{{NAME}}", name)
            html_template = html_template.replace("{{EMAIL}}", email)
            html_template = html_template.replace("{{PHONE}}", phone)
            html_template = html_template.replace("{{SUMMARY}}", resume_data.get("summary", ""))
            return html_template

        # Inline fallback HTML
        skills = resume_data.get("skills", {})
        skills_html = ""
        for cat, items in skills.items():
            if items:
                skills_html += f"<p><strong>{cat.title()}:</strong> {', '.join(items)}</p>"

        exp_html = ""
        for exp in resume_data.get("experience", []):
            bullets = "".join(f"<li>{b}</li>" for b in exp.get("bullets", []))
            exp_html += f"""
            <div class="entry">
                <h3>{exp.get('role', '')} — {exp.get('company', '')}</h3>
                <p class="date">{exp.get('duration', '')}</p>
                <ul>{bullets}</ul>
            </div>"""

        proj_html = ""
        for proj in resume_data.get("projects", []):
            bullets = "".join(f"<li>{b}</li>" for b in proj.get("bullets", []))
            proj_html += f"""
            <div class="entry">
                <h3>{proj.get('name', '')} <span class="tech">| {proj.get('tech_stack', '')}</span></h3>
                <ul>{bullets}</ul>
            </div>"""

        edu_html = ""
        for edu in resume_data.get("education", []):
            edu_html += f"""
            <div class="entry">
                <h3>{edu.get('degree', '')} — {edu.get('institution', '')}</h3>
                <p>{edu.get('year', '')} | CGPA: {edu.get('cgpa', 'N/A')}</p>
            </div>"""

        certs = resume_data.get("certifications", [])
        certs_html = "".join(f"<li>{c}</li>" for c in certs)

        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: 'Calibri', 'Helvetica', sans-serif; margin: 40px 50px;
         font-size: 11pt; line-height: 1.4; color: #333; }}
  h1 {{ text-align: center; margin-bottom: 2px; color: #1a1a2e; font-size: 22pt; }}
  .contact {{ text-align: center; color: #666; margin-bottom: 20px; }}
  h2 {{ color: #16213e; border-bottom: 2px solid #0f3460; padding-bottom: 4px;
       font-size: 13pt; margin-top: 18px; }}
  h3 {{ margin-bottom: 2px; font-size: 11pt; }}
  .date {{ color: #888; font-style: italic; margin-top: 0; }}
  .tech {{ color: #666; font-weight: normal; font-size: 10pt; }}
  ul {{ margin-top: 4px; padding-left: 20px; }}
  li {{ margin-bottom: 3px; }}
  .entry {{ margin-bottom: 12px; }}
</style></head><body>
<h1>{name}</h1>
<p class="contact">{email} | {phone}</p>
<h2>Professional Summary</h2>
<p>{resume_data.get('summary', '')}</p>
<h2>Technical Skills</h2>
{skills_html}
<h2>Experience</h2>
{exp_html}
<h2>Projects</h2>
{proj_html}
<h2>Education</h2>
{edu_html}
{"<h2>Certifications</h2><ul>" + certs_html + "</ul>" if certs else ""}
</body></html>"""

    def _write_text_fallback(self, resume_data: dict, output_path: str,
                             contact_info: dict = None):
        """Write a plain text version as fallback when WeasyPrint fails."""
        import json
        with open(output_path.replace(".pdf", ".txt"), "w", encoding="utf-8") as f:
            f.write(json.dumps(resume_data, indent=2))


file_builder = FileBuilder()
