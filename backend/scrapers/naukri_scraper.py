"""Naukri.com scraper — requests + BeautifulSoup."""

import logging
import requests
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class NaukriScraper(BaseScraper):
    """Scrape job listings from Naukri.com public pages."""

    BASE_URL = "https://www.naukri.com/{role}-jobs-in-{location}"

    def scrape(self, role: str, location: str = "india",
               max_jobs: int = 25) -> list[dict]:
        """Scrape jobs from Naukri.com."""
        url = self.BASE_URL.format(
            role=role.lower().replace(" ", "-"),
            location=location.lower().replace(" ", "-"),
        )
        jobs = []

        try:
            self.respectful_delay()
            resp = requests.get(url, headers=self.get_headers(), timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Naukri uses various card selectors; try multiple
            cards = soup.select("article.jobTuple")[:max_jobs]
            if not cards:
                cards = soup.select(".srp-jobtuple-wrapper")[:max_jobs]
            if not cards:
                cards = soup.select("[class*='jobTuple']")[:max_jobs]

            for card in cards:
                try:
                    title_el = card.select_one(".title, a.title, [class*='title']")
                    company_el = card.select_one(".subTitle, .comp-name, [class*='comp']")
                    link_el = card.select_one("a[href*='naukri.com']")
                    location_el = card.select_one(".location, .loc, [class*='loc']")

                    title = title_el.get_text(strip=True) if title_el else None
                    company = company_el.get_text(strip=True) if company_el else None
                    job_url = link_el["href"] if link_el and link_el.has_attr("href") else ""
                    loc = location_el.get_text(strip=True) if location_el else ""

                    if title and company:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": loc,
                            "job_url": job_url,
                            "jd_text": "",  # Would need detail page scrape
                            "source": "naukri",
                        })

                    self.respectful_delay(0.5, 1.5)

                except Exception as e:
                    logger.debug(f"Naukri card parse error: {e}")
                    continue

            logger.info(f"Naukri: scraped {len(jobs)} jobs for '{role}' in '{location}'")

        except Exception as e:
            logger.error(f"Naukri scrape error: {e}")

        return jobs
