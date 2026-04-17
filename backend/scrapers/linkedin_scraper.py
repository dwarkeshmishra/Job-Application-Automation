"""LinkedIn scraper — Playwright-based (placeholder).

NOTE: LinkedIn scraping is complex and requires Playwright with headless browser.
This is a placeholder that returns empty results if Playwright is not available.
The Chrome Extension is the recommended way to capture LinkedIn jobs.
"""

import logging

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """Placeholder LinkedIn scraper using Playwright."""

    async def scrape(self, role: str, location: str = "india",
                     max_jobs: int = 25) -> list[dict]:
        """
        Scrape LinkedIn jobs.

        NOTE: LinkedIn heavily blocks automated scraping.
        Recommend using the Chrome Extension for LinkedIn job capture instead.
        """
        jobs = []

        try:
            from playwright.async_api import async_playwright

            search_url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={role.replace(' ', '%20')}"
                f"&location={location.replace(' ', '%20')}"
                f"&position=1&pageNum=0"
            )

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(search_url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)  # Wait for JS rendering

                cards = await page.query_selector_all(".base-card")

                for card in cards[:max_jobs]:
                    try:
                        title = await card.query_selector(".base-search-card__title")
                        company = await card.query_selector(".base-search-card__subtitle")
                        loc = await card.query_selector(".job-search-card__location")
                        link = await card.query_selector("a.base-card__full-link")

                        jobs.append({
                            "title": await title.inner_text() if title else "",
                            "company": await company.inner_text() if company else "",
                            "location": await loc.inner_text() if loc else "",
                            "job_url": await link.get_attribute("href") if link else "",
                            "jd_text": "",
                            "source": "linkedin",
                        })
                    except Exception:
                        continue

                await browser.close()

            logger.info(f"LinkedIn: scraped {len(jobs)} jobs for '{role}'")

        except ImportError:
            logger.warning("Playwright not installed. Use Chrome Extension for LinkedIn jobs.")
        except Exception as e:
            logger.error(f"LinkedIn scrape error: {e}")

        return jobs
