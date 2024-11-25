import threading
import logging
from scrapers import articlefactory, yellowpages, procurement, googlejobs, grants

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingTask:
    VALID_SCRAPERS = {"yellowpages", "grants", "article_factory", "google_jobs", "procurement"}

    def __init__(self, database, scraper_name=""):
        self.scrape_name = scraper_name
        self.status = "not_started"
        self.available = True
        self.db = database
        self.state = None
        self.category = None
        self._lock = threading.Lock()

    def start(self, scraper_name, state=None, category=None):
        """Start the specified scraper in a separate thread."""
        if scraper_name not in self.VALID_SCRAPERS:
            with self._lock:
                self.status = "invalid_scraper"
                self.available = True
            return f"Invalid scraper name: {scraper_name}"

        with self._lock:
            self.scrape_name = scraper_name
            self.status = "in_progress"
            self.available = False
            self.state = state
            self.category = category

        # Dynamically find and execute the scraper function
        func = getattr(self, f"run_{scraper_name}", None)
        if func:
            thread = threading.Thread(target=func, args=(self.db, self.run_after_thread, state, category))
            thread.start()
            return f"Running {self.scrape_name} function in non-blocking mode"

    def get_status(self):
        """Get the current status of the scraper."""
        with self._lock:
            return {
                "scraper_name": self.scrape_name,
                "status": self.status,
                "available": self.available,
                "state": self.state,
                "category": self.category,
            }

    def run_after_thread(self, status="completed"):
        """Callback method to update the status after thread completion."""
        with self._lock:
            self.status = status
            self.available = True

    def run_yellowpages(self, database, callback, state=None, category=None):
        """Run the Yellow Pages scraper."""
        try:
            logger.info("Starting Yellow Pages scraper...")
            scraper = yellowpages.YellowPagesScrape(db=database)
            scraper.start(state=state, category=category)
            logger.info("Yellow Pages scraper completed.")
        except Exception as e:
            logger.error(f"Error in Yellow Pages scraper: {e}")
            self.run_after_thread(status="failed")
        else:
            callback()

    def run_grants(self, database, callback, state=None, category=None):
        """Run the Grants scraper."""
        try:
            logger.info("Starting Grants scraper...")
            scraper = grants.GrantsScrape(db=database)
            scraper.start()
            logger.info("Grants scraper completed.")
        except Exception as e:
            logger.error(f"Error in Grants scraper: {e}")
            self.run_after_thread(status="failed")
        else:
            callback()

    def run_article_factory(self, database, callback, state=None, category=None):
        """Run the Article Factory scraper."""
        try:
            logger.info("Starting Article Factory scraper...")
            scraper = articlefactory.ArticleFactoryScrape(db=database)
            scraper.start()
            logger.info("Article Factory scraper completed.")
        except Exception as e:
            logger.error(f"Error in Article Factory scraper: {e}")
            self.run_after_thread(status="failed")
        else:
            callback()

    def run_google_jobs(self, database, callback, state=None, category=None):
        """Run the Google Jobs scraper."""
        try:
            logger.info("Starting Google Jobs scraper...")
            scraper = googlejobs.GoogleJobsScraper(db=database)
            scraper.start()
            logger.info("Google Jobs scraper completed.")
        except Exception as e:
            logger.error(f"Error in Google Jobs scraper: {e}")
            self.run_after_thread(status="failed")
        else:
            callback()

    def run_procurement(self, database, callback, state=None, category=None):
        """Run the Procurement scraper."""
        try:
            logger.info("Starting Procurement scraper...")
            scraper = procurement.ProcurementScrape(db=database)
            scraper.start()
            logger.info("Procurement scraper completed.")
        except Exception as e:
            logger.error(f"Error in Procurement scraper: {e}")
            self.run_after_thread(status="failed")
        else:
            callback()

    def stop(self):
        """Stop the current task (optional implementation)."""
        with self._lock:
            if not self.available:
                self.status = "stopped"
                self.available = True
                logger.info(f"Scraper {self.scrape_name} has been stopped.")
            else:
                logger.info("No active scraper to stop.")
