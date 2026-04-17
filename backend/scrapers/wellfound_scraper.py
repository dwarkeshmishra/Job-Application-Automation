"""Wellfound (AngelList Talent) scraper."""

import logging
import requests
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class WellfoundScraper(BaseScraper):
    """Scrape startup job listings from Wellfound."""

    BASE_URL = "https://wellfound.com/role/{role}"

    def scrape(self, role: str, max_jobs: int = 25) -> list[dict]:
        """Scrape jobs from Wellfound."""
        url = self.BASE_URL.format(role=role.lower().replace(" ", "-"))
        jobs = []

        try:
            self.respectful_delay()
            resp = requests.get(url, headers=self.get_headers(), timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.select("[class*='styles_jobListing'], .job-listing")[:max_jobs]

            for card in cards:
                try:
                    title_el = card.select_one("a[class*='jobTitle'], h2, .title")
                    company_el = card.select_one("[class*='company'], .startup-name")
                    location_el = card.select_one("[class*='location'], .location")

                    title = title_el.get_text(strip=True) if title_el else None
                    company = company_el.get_text(strip=True) if company_el else None
                    loc = location_el.get_text(strip=True) if location_el else ""

                    job_url = ""
                    if title_el and title_el.has_attr("href"):
                        href = title_el["href"]
                        job_url = f"https://wellfound.com{href}" if href.startswith("/") else href

                    if title and company:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": loc,
                            "job_url": job_url,
                            "jd_text": "",
                            "source": "wellfound",
                        })

                    self.respectful_delay(0.5, 1.5)

                except Exception as e:
                    logger.debug(f"Wellfound card parse error: {e}")
                    continue

            logger.info(f"Wellfound: scraped {len(jobs)} jobs for '{role}'")

        except Exception as e:
            logger.error(f"Wellfound scrape error: {e}")

        return jobs
