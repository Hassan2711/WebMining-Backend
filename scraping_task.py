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

    # def update_progress(self):
    #     self.available = False
    #     self.status = "in_progress"
    #     # self.scraped_data.extend(data)
    #     # self.progress = (self.current_source_index + 1) / len(self.sources) * 100
    #     # if self.progress == 100:
    #     #     self.status = "completed"

    def start(self, scraper_name):
        self.scrape_name = scraper_name
        self.status = "in_progress"
        self.available = False

        # Process the response here
        if self.scrape_name == "yellowpages":
            # Create a new thread to run the yellow_pages function
            func = self.run_yellow_pages
        elif self.scrape_name == "grants":
            # Create a new thread to run the grants function
            func = self.run_grants
        elif self.scrape_name == "article_factory":
            # Create a new thread to run the article_factory function
            func = self.run_article_factory
        elif self.scrape_name == "google_jobs":
            # Create a new thread to run the google_jobs function
            func = self.run_google_jobs
        elif self.scrape_name == "procurement":
            # Create a new thread to run the procurement function
            func = self.run_procurement
        else:
            self.status = "invalid_scraper"
            self.available = True
            return "Invalid scraper name"
        
        thread = threading.Thread(
            target=func,
            args=(self.db, self.run_after_thread)
        )
        
        thread.start()
        # Return the response immediately
        return "Running yellow_pages function in non-blocking mode"

    def get_status(self):
        return {
            "scraper_name": self.scrape_name,
            "status": self.status,
            "available": self.available
        }
        
    def run_after_thread(self):
        self.complete()

    def complete(self):
        self.status = "completed"
        self.available = True
    
    # Define the functions to run in the new thread
    
    def run_yellow_pages(self, database, callback):
        scraper = yellowpages.YellowPagesScrape(db=database)
        scraper.start()
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
        # TODO: fix this
        try:
            scraper = googlejobs.GoogleJobsScraper(db=database)
            scraper.start()
            callback()
        except Exception as e:
            print(e)
        
        
    def run_procurement(self, database, callback):
        scraper = procurement.ProcurementScrape(db=database)
        scraper.start()
        callback()

    def sent_to_airtable(self, table_name, data):
        if table_name in ["grants", "google_jobs", "procurement"]:
            airtable.save_to_local_work(data)
        elif table_name in ["yellowpages", "article_factory"]:
            airtable.save_to_ba_trips(data)

