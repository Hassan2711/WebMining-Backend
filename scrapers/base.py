

class BaseScraper:
    def __init__(self, name='', url=None, db=None):
        self.name = name
        self.url = url
        self.db = db

    def start(self):
        # Implement your scraping logic here
        pass

    def save(self, data):
        # Implement your saving logic here
        pass

    def stop(self):
        # Implement your stopping logic here
        pass
