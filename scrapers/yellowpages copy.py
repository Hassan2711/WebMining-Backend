import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from .base import BaseScraper

def scrape_yellowpages(total_pages=None, search_for=None,  state=None):
    print("Scraping Yellow Pages")
    print(state)

    total_pages = "10" if total_pages is None else total_pages
    search_for = "Restaurants" if search_for is None else search_for
    # city = "San Francisco" if city is None else city
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
                # f'https://www.yellowpages.com/search?search_terms={search_for}&geo_location_terms={city}%2C+{state}&page={page}').text
                f'https://www.yellowpages.com/search?search_terms={search_for}&geo_location_terms={ }&page={page}').text
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
    def __init__(self, **kwargs):
        super().__init__(name='yellowpages', **kwargs)

    def start(self, state=None, category=None):
        print("Scraping Yellow Pages started...")
        data = scrape_yellowpages(search_for=category, state=state)
        # print('',len(data))
        if len(data) > 0:
            self.save(data)
            print(data)
        else:
            print("No data found")

    def save(self, data):
        print("Saving Yellow Pages data...")
        collection = self.db["yellowpages"]

        # Add today's date to each item in data
        date = datetime.now()
        for item in data:
            item['date'] = date

        # Filter out items with empty or null 'name' field to avoid duplicates
        data = [item for item in data if item.get('Name')]

        print('Uploading data to MongoDB...')
        # Create a unique index on 'Name' and 'Link' to avoid duplicates
        collection.create_index([('Name', 1), ('Link', 1)], unique=True)

        try:
            collection.insert_many(data, ordered=False)
            print('Data uploaded successfully.')
        except Exception as e:
            print(f"Error inserting data: {e}. Possible duplicates or insertion issue.")


    def stop(self):
        pass
