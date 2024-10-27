import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from .base import BaseScraper

def scrape_yellowpages(total_pages=None, search_for=None, city=None, state=None):
    print("Scraping Yellow Pages")
    total_pages = "10" if total_pages is None else total_pages
    search_for = "Restaurants" if search_for is None else search_for
    city = "San Francisco" if city is None else city
    state = "CA" if state is None else state

    # Creating dataframe
    df = {'Name': [],
          'Phone': [],
          'Address': [],
          'Link': []
          }

    df = pd.DataFrame(df)

    # Scraping data
    results = []

    for page in range(1, int(total_pages) + 1):
        print(f'Scraping page {page}...')
        try:
            html_text = requests.get(
                f'https://www.yellowpages.com/search?search_terms={search_for}&geo_location_terms={city}%2C+{state}&page={page}').text
            soup = BeautifulSoup(html_text, 'lxml')
            listings = soup.find('div', class_='search-results organic').find_all('div', class_='result')
            for index, listing in enumerate(listings):
                try:
                    name = listings[index].div.div.find('div', class_='info').find('div',
                                                                                     class_='info-section info-primary').h2.a.span.text
                    phone = listings[index].div.div.find('div', class_='info').find('div',
                                                                                      class_='info-section info-secondary').find(
                        'div', class_='phones phone primary').text
                    street_address = listings[index].div.div.find('div', class_='info').find('div',
                                                                                              class_='info-section info-secondary').find(
                        'div', class_='adr').find('div', class_='street-address').text
                    locality = listings[index].div.div.find('div', class_='info').find('div',
                                                                                         class_='info-section info-secondary').find(
                        'div', class_='adr').find('div', class_='locality').text
                    link = listings[index].div.div.find('div', class_='info').find('div',
                                                                                    class_='info-section info-primary').h2.a.get(
                        'href')

                    results.append({
                        'Name': name,
                        'Phone': phone,
                        'Address': f'{street_address}, {locality}',
                        'Link': f'www.yellowpages.com{link}'
                    })

                except:
                    pass
            if page == 1:
                print(f'Page {page} done.')
            else:
                print(f'Page {page} done.')
        except Exception as e:
            print(e)
            print(f'Error on page {page}.')

    return results


class YellowPagesScrape(BaseScraper):
    def __init__(self, database, url=None):
        super().__init__(url, database)

    def start(self):
        print("Scraping Yellow Pages started...")
        data = scrape_yellowpages()
        # print('',len(data))
        self.save(data)

    def save(self, data):
        print("Saving Yellow Pages data...")
        collection = self.db["yellowpages"]
        # add today's date to the data
        for item in data:
            item['date'] = datetime.now() 
        print('uploading data')
        collection.insert_many(data)
        print('data uploaded')

    def stop(self):
        pass
