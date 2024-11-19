import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
from datetime import datetime
from .base import BaseScraper

def get_detailed_info(link):
    # Initialize headless Chrome driver
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
       # Initialize all expected fields with empty strings
    details = {
        'email': '',
        'regular_hours': '',
        'claimed': '',
        'general_info': '',
        'services_products': '',
        'neighborhoods': '',
        'amenities': '',
        'languages': '',
        'aka': '',
        'social_links': '',
        'categories': '',
        'photos_url': 'NA',
        'other_info': '',
        'other_links': ''
    }

    try:
        driver.get(link)
        
        # Extract email
        try:
            email = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//a[@class='email-business']"))
            ).get_attribute('href').split('mailto:')[1]
            details['email'] = email
        except (NoSuchElementException, TimeoutException, IndexError):
            details['email'] = ''
        
        # Extract regular hours
        try:
            regular_hours = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="aside-hours"]/dd/div/table'))
            ).text.replace('\n', ' | ')
            details['regular_hours'] = regular_hours
        except (NoSuchElementException, TimeoutException):
            details['regular_hours'] = ''
        
        # Other fields follow similar pattern
        fields = {
            "claimed": "//div[@id='claimed']",
            "general_info": "//dd[@class='general-info']",
            "services_products": "//dd[@class='features-services']",
            "neighborhoods": "//dd[@class='neighborhoods']",
            "amenities": "//dd[@class='amenities']",
            "languages": "//dd[@class='languages']",
            "aka": "//dd[@class='aka']//p[1]",
            "social_links": "//dd[@class='social-links']",
            "categories": "//dd[@class='categories']//div[@class='categories']",
            "other_info": "//dd[@class='other-information']",
            "other_links": "//dd[@class='weblinks']"
        }
        
        for key, xpath in fields.items():
            try:
                details[key] = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                ).text
            except (NoSuchElementException, TimeoutException):
                details[key] = ''
                
        # Photos URL
        try:
            section_title = driver.find_element(By.CLASS_NAME, 'section-title')
            link_element = section_title.find_element(By.TAG_NAME, 'a')
            details['photos_url'] = link_element.get_attribute('href')
        except (NoSuchElementException, TimeoutException):
            details['photos_url'] = 'NA'
        
    finally:
        driver.quit()
    return details

def scrape_yellowpages(total_pages=None, search_for=None, state=None):
    print("Scraping Yellow Pages")
    total_pages = "10" if total_pages is None else total_pages
    search_for = "Restaurants" if search_for is None else search_for
    state = "CA" if state is None else state

    results = []

    for page in range(1, int(total_pages) + 1):
        print(f'Scraping page {page}...')
        try:
            html_text = requests.get(
                f'https://www.yellowpages.com/search?search_terms={search_for}&geo_location_terms={state}&page={page}'
            ).text
            soup = BeautifulSoup(html_text, 'lxml')
            listings = soup.find('div', class_='search-results organic').find_all('div', class_='result')
            
            for listing in listings:
                try:
                    name = listing.find('a', class_='business-name').text
                    phone = listing.find('div', class_='phones phone primary').text
                    address = listing.find('div', class_='street-address').text + ', ' + listing.find('div', class_='locality').text
                    link = 'https://www.yellowpages.com' + listing.find('a', class_='business-name')['href']
                    
                    # Get additional details with Selenium
                    detailed_info = get_detailed_info(link)
                    result = {
                        'Name': name,
                        'Phone': phone,
                        'Address': address,
                        'Link': link,
                        'email': detailed_info['email'],
                        "regular_hours": detailed_info['regular_hours'],
                        "claimed": detailed_info['claimed'],
                        "general_info": detailed_info['general_info'],
                        "services_products": detailed_info['services_products'],
                        "neighborhoods": detailed_info['neighborhoods'],
                        "amenities": detailed_info['amenities'],
                        "languages": detailed_info['languages'],
                        "aka": detailed_info['aka'],
                        "social_links": detailed_info['social_links'],
                        "categories": detailed_info['categories'],
                        "photos_url": detailed_info['photos_url'],
                        "other_info": detailed_info['other_info'],
                        "other_links": detailed_info['other_links'],
                        # **detailed_info
                    }
                    results.append(result)
                    # Set the status within the same result dictionary
                    if detailed_info['email'] != '' and detailed_info['general_info'] != '' and detailed_info['regular_hours']:
                        result['status'] = 'Approved'
                    else:
                        result['status'] = 'Rejected'
                                        
                except Exception as e:
                    print(f"Error processing listing: {e}")

        except Exception as e:
            print(f'Error on page {page}: {e}')

    return results

class YellowPagesScrape(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(name='yellowpages', **kwargs)

    def start(self, state=None, category=None):
        print("Scraping Yellow Pages started...")
        data = scrape_yellowpages(search_for=category, state=state)
        
        if data:
            self.save(data)
            print("Data saved successfully.")
        else:
            print("No data found")

    def save(self, data):
        print("Saving Yellow Pages data...")
        collection = self.db["yellowpages"]
        date = datetime.now()
        for item in data:
            item['date'] = date
            print("Document to Insert:", item) 
        
        # Avoid duplicates by unique index on Name and Link
        collection.create_index([('Name', 1), ('Link', 1)], unique=True)
        
        try:
            collection.insert_many(data, ordered=False)
            print('Data uploaded successfully.')
        except Exception as e:
            print(f"Error inserting data: {e}. Possible duplicates or insertion issue.")

    def stop(self):
        pass
