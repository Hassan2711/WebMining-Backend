from .base import BaseScraper
from selenium import webdriver
from datetime import datetime
from parsel import Selector
import pandas as pd
import time
import json
import os

REMOTE_DRIVER = os.getenv('REMOTE_DRIVER')


def scroll_page(url):
    # Set the desired capabilities for the browser
    # Create a remote WebDriver instance    
    # options = webdriver.ChromeOptions()
    options = webdriver.FirefoxOptions()
    options.headless = True
    options.add_argument("--lang=en")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Remote(
        command_executor=REMOTE_DRIVER,
        options=options
    )
    driver.get(url)
    
    old_height = driver.execute_script("""
    	function getHeight() {
    		return document.querySelector('.zxU94d').scrollHeight;
    	}
    	return getHeight();
    """)
    
    while True:
        print("Scrolling...")
        driver.execute_script("document.querySelector('.zxU94d').scrollTo(0, document.querySelector('.zxU94d').scrollHeight)")

        time.sleep(5)

        new_height = driver.execute_script("""
            function getHeight() {
                return document.querySelector('.zxU94d').scrollHeight;
            }
            return getHeight();
        """)

        if new_height == old_height:
            break

        old_height = new_height
        
        print("New height:", new_height)
        # break
    
    selector = Selector(driver.page_source)
    driver.quit()
    
    return selector
		
def scraper(selector):	
    google_jobs_results = []
    
    for result in selector.css('.iFjolb'):
        title = result.css('.BjJfJf::text').get()
        company = result.css('.vNEEBe::text').get()
        
        container = result.css('.Qk80Jf::text').getall()
        location = container[0]
        via = container[1]
        
        # thumbnail = result.css('.pJ3Uqf img::attr(src)').get()
        extensions = result.css('.KKh3md span::text').getall()
        
        google_jobs_results.append({
            'title': title,
            'company': company,
            'location': location,
            'via': via,
            # 'thumbnail': thumbnail,
            'extensions': extensions
        })
    
    print(json.dumps(google_jobs_results, indent=2, ensure_ascii=False))
    df = pd.DataFrame(google_jobs_results)
    # df.to_excel('google-jobs.xlsx', index=False)
    print(len(google_jobs_results), type(google_jobs_results))

    # # Convert DataFrame to dictionary (optional)
    data = df.to_dict(orient="records")
    print("Data converted to dictionary")
    return data

def scrape_google():
    params = {
        'q': 'San Fransisco',					    # search string
        'ibp': 'htl;jobs',							# google jobs
        'uule': 'w+CAIQICINVW5pdGVkIFN0YXRlcw',		# encoded location (USA)
        'hl': 'en',									# language 
        'gl': 'us',									# country of the search
    }
	
    URL = f"https://www.google.com/search?q={params['q']}&ibp={params['ibp']}&uule={params['uule']}&hl={params['hl']}&gl={params['gl']}"
    result = scroll_page(URL)
    jobs_data = scraper(result)
    return jobs_data


class GoogleJobsScraper(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(name='google', **kwargs)
        
    def start(self):
        print("Scraping Google Jobs started...")
        data = scrape_google()
        self.save(data)
        
    def save(self, data):
        collection = self.db["google_jobs"]
        # add today's date to the data
        date = datetime.now()
        for item in data:
            item['date'] = date
        print('uploading data')
        collection.create_index([('name', 1)], unique=True)
        try: 
            collection.insert_many(data, ordered=False)
        except Exception as e:
            print("Duplicated found!")
        print("Data saved to MongoDB")
        
    def stop(self):
        print("Scraping Google stopped...")


# class GoogleJobsScraper:
#     def __init__(self, **kwargs):
#         self.db = kwargs.get("db")
#         self.url = "https://careers.google.com/jobs/results/"
#         self.scrape_name = "google_jobs"
#         self.status = "running"
#         self.available = False