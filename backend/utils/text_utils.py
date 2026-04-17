"""Text cleaning and processing utilities."""

import re
import unicodedata


def clean_text(text: str) -> str:
    """Clean and normalize text from scraped/parsed content."""
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove special control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def truncate(text: str, max_length: int = 500) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def extract_email(text: str) -> str | None:
    """Extract first email address from text."""
    match = re.search(r"[\w.-]+@[\w.-]+\.\w+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Extract first phone number from text."""
    match = re.search(r"[+\d][\d\s\-()]{8,15}", text)
    return match.group(0).strip() if match else None


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:50]
