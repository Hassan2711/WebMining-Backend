from . import (
    articlefactory as af,
    googlejobs as gj,
    grants as g,
    procurement as p,
    yellowpages as yp
)

class Runner:
    """
    Class to run the scrapers
    """
    def __init__(self, db):
        self.db = db
    
    def run_yellow_pages(self):
        """
        Run the yellow pages scraper
        """
        status = True
        try:
            scraper = yp.YellowPagesScrape(db=self.db)
            scraper.start()
        except:
            status = False
        return status
    
    def run_grants(self):
        """
        Run the grants scraper
        """
        status = True
        try:
            scraper = g.GrantsScrape(db=self.db)
            scraper.start()
        except:
            status = False
        return status
    
    def run_article_factory(self):
        """
        Run the article factory scraper
        """
        status = True
        try:
            scraper = af.ArticleFactoryScrape(db=self.db)
            scraper.start()
        except:
            status = False
        return status
    
    def run_google_jobs(self):
        """
        Run the google jobs scraper
        """
        status = True
        try:
            scraper = gj.GoogleJobsScrape(db=self.db)
            scraper.start()
        except:
            status = False
        return status
    
    def run_procurement(self):
        """
        Run the procurement scraper
        """
        status = True
        try:
            scraper = p.ProcurementScrape(db=self.db)
            scraper.start()
        except:
            status = False
        return status
    