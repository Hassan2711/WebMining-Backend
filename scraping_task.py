from scrapers import articlefactory
from scrapers import yellowpages
from scrapers import procurement
from scrapers import googlejobs
from scrapers import grants
import threading
from airtable import Airtable

# Airtable API
airtable = Airtable()

class ScrapingTask:
    def __init__(self, database, scraper_name=""):
        self.scrape_name = scraper_name
        self.status = "not_started"
        self.available = True
        self.db = database

    def start(self, scraper_name, state=None, category=None):
        self.scrape_name = scraper_name
        self.status = "in_progress"
        self.available = False
        self.state = state
        self.category = category  # Fixed the typo here

        # Choose which scraper function to run based on the scraper name
        if self.scrape_name == "yellowpages":
            func = self.run_yellow_pages
            args = (self.db, self.run_after_thread, state, category)
        elif self.scrape_name == "grants":
            func = self.run_grants
            args = (self.db, self.run_after_thread)
        elif self.scrape_name == "article_factory":
            func = self.run_article_factory
            args = (self.db, self.run_after_thread)
        elif self.scrape_name == "google_jobs":
            func = self.run_google_jobs
            args = (self.db, self.run_after_thread)
        elif self.scrape_name == "procurement":
            func = self.run_procurement
            args = (self.db, self.run_after_thread)
        else:
            self.status = "invalid_scraper"
            self.available = True
            return "Invalid scraper name"
        
        # Start the scraper in a new thread
        thread = threading.Thread(target=func, args=args)
        thread.start()

        # Return immediately while the thread continues running
        return f"Running {self.scrape_name} function in non-blocking mode"

    def get_status(self):
        return {
            "scraper_name": self.scrape_name,
            "status": self.status,
            "available": self.available,
            "state": self.state,
            "category": self.category  # Ensure category is included in the status
        }

    def run_after_thread(self):
        self.complete()

    def complete(self):
        self.status = "completed"
        self.available = True

    # Define the scraper functions
    def run_yellow_pages(self, database, callback, state=None, category=None):
        scraper = yellowpages.YellowPagesScrape(db=database)
        scraper.start(state=state, category=category)
        callback()

    def run_grants(self, database, callback):
        scraper = grants.GrantsScrape(db=database)
        scraper.start()
        callback()

    def run_article_factory(self, database, callback):
        scraper = articlefactory.ArticleFactoryScrape(db=database)
        scraper.start()
        callback()

    def run_google_jobs(self, database, callback):
        try:
            scraper = googlejobs.GoogleJobsScraper(db=database)
            scraper.start()
            callback()
        except Exception as e:
            print(f"Error running Google Jobs scraper: {e}")
            self.status = "failed"
            self.available = True
            callback()  # Ensure the callback is called after failure to update status

    def run_procurement(self, database, callback):
        scraper = procurement.ProcurementScrape(db=database)
        scraper.start()
        callback()

    def sent_to_airtable(self, table_name, data):
        if table_name in ["grants", "google_jobs", "procurement"]:
            airtable.save_to_local_work(data)
        elif table_name in ["yellowpages", "article_factory"]:
            airtable.save_to_ba_trips(data)
        else:
            print(f"Unknown table name: {table_name}")
