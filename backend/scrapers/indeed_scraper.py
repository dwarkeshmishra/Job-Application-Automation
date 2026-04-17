"""Indeed India scraper — requests + BeautifulSoup."""

import logging
import requests
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    """Scrape job listings from Indeed India public pages."""

    BASE_URL = "https://in.indeed.com/jobs"

    def scrape(self, role: str, location: str = "india",
               max_jobs: int = 25) -> list[dict]:
        """Scrape jobs from Indeed India."""
        jobs = []

        try:
            self.respectful_delay()
            resp = requests.get(
                self.BASE_URL,
                params={"q": role, "l": location, "limit": max_jobs},
                headers=self.get_headers(),
                timeout=15,
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.select(".job_seen_beacon, .jobsearch-ResultsList > li")[:max_jobs]

            for card in cards:
                try:
                    title_el = card.select_one("h2 a, .jobTitle a, [class*='jobTitle']")
                    company_el = card.select_one("[data-testid='company-name'], .companyName")
                    location_el = card.select_one("[data-testid='text-location'], .companyLocation")

                    title = title_el.get_text(strip=True) if title_el else None
                    company = company_el.get_text(strip=True) if company_el else None
                    loc = location_el.get_text(strip=True) if location_el else ""

                    job_url = ""
                    if title_el and title_el.has_attr("href"):
                        href = title_el["href"]
                        job_url = f"https://in.indeed.com{href}" if href.startswith("/") else href

                    # Snippet
                    snippet_el = card.select_one(".job-snippet, [class*='snippet']")
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""

                    if title and company:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": loc,
                            "job_url": job_url,
                            "jd_text": snippet,
                            "source": "indeed",
                        })

                    self.respectful_delay(0.5, 1.5)

                except Exception as e:
                    logger.debug(f"Indeed card parse error: {e}")
                    continue

            logger.info(f"Indeed: scraped {len(jobs)} jobs for '{role}' in '{location}'")

        except Exception as e:
            logger.error(f"Indeed scrape error: {e}")

        return jobs
