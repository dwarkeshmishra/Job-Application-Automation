"""File and path utility functions."""

import os
import shutil
from pathlib import Path
from config import settings


def ensure_dirs():
    """Ensure all required data directories exist."""
    dirs = [
        settings.data_path / "resumes",
        settings.data_path / "exports",
        settings.data_path / "uploads",
        settings.data_path / "db",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def get_resume_dir(company: str) -> Path:
    """Get or create the resume directory for a company."""
    slug = company.lower().replace(" ", "_").replace(".", "")
    path = settings.data_path / "resumes" / slug
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_upload_path(filename: str) -> Path:
    """Get the upload path for a file."""
    return settings.data_path / "uploads" / filename


def safe_filename(filename: str) -> str:
    """Sanitize a filename to be filesystem-safe."""
    import re
    name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return name[:200]  # Limit length


def get_file_size_mb(path: str) -> float:
    """Get file size in MB."""
    return os.path.getsize(path) / (1024 * 1024)
