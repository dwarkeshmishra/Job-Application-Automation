"""Remotive.io free API scraper — no authentication needed."""

import logging
import httpx

logger = logging.getLogger(__name__)


class RemotiveScraper:
    """Scrape remote jobs from Remotive.io free API."""

    API_URL = "https://remotive.com/api/remote-jobs"

    async def scrape(self, role: str, max_jobs: int = 25) -> list[dict]:
        """Fetch remote jobs from Remotive API."""
        jobs = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(self.API_URL, params={
                    "search": role,
                    "limit": max_jobs,
                })
                resp.raise_for_status()

            data = resp.json()
            for j in data.get("jobs", [])[:max_jobs]:
                # Strip HTML tags from description
                import re
                desc = re.sub(r"<[^>]+>", "", j.get("description", ""))

                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company_name", ""),
                    "location": j.get("candidate_required_location", "Remote"),
                    "job_url": j.get("url", ""),
                    "jd_text": desc[:3000],
                    "job_type": j.get("job_type", "full_time"),
                    "source": "remotive",
                })

            logger.info(f"Remotive: fetched {len(jobs)} jobs for '{role}'")

        except Exception as e:
            logger.error(f"Remotive scrape error: {e}")

        return jobs
