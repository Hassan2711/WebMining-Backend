from .base import BaseScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import pandas as pd
import time
import os

REMOTE_DRIVER = os.getenv('REMOTE_DRIVER')

def scrape_grants():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome()  # Assuming you want to run this locally
    table_data = []
    filtered_urls = []

    try:
        url = "https://www.grants.gov/search-grants"
        driver.get(url)
        time.sleep(3)
        driver.maximize_window()
        
        page_count = 0

        while len(driver.find_elements(By.TAG_NAME, "tr")) > 3:
            page_count += 1
            print(f"Scraping page {page_count}...")
            time.sleep(2)

            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            body.send_keys(Keys.END)
            time.sleep(2)
            body.send_keys(Keys.HOME)

            table_element = driver.find_element(By.XPATH, "//*[@id='__nuxt']/div[4]/div/div/div/div[2]/div[3]/table")
            page_data = []

            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "/search-results-detail/" in href:
                    filtered_urls.append(href)

            for row in table_element.find_elements(By.TAG_NAME, "tr"):
                row_data = []
                for cell in row.find_elements(By.TAG_NAME, "td"):
                    cell_text = cell.text.strip()
                    row_data.append(cell_text)
                page_data.append(row_data)

            filtered_list = page_data[2:-1]
            print(len(filtered_list), filtered_list)
            table_data.extend(filtered_list)

            print(f"Total data extracted: {len(table_data)}")

            next_button = driver.find_elements(By.XPATH, "//th[@class='bg-white']//span[@class='usa-pagination__link-text'][normalize-space()='Next']")
            print(f"Next button found: {bool(next_button)}")
            if next_button:
                body.send_keys(Keys.END)
                time.sleep(2)
                next_button[0].click()
                time.sleep(2)
            else:
                print("No more pages to scrape.")
                break

        print(f"Total pages scraped: {page_count}")
        print(f"Total data extracted: {len(table_data)}")
    except Exception as e:
        print(f"url: {url}")
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Driver quit.")
        return table_data, filtered_urls


class GrantsScrape(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(name='grants', **kwargs)
        
    def start(self):
        print("Scraping Grants started...")
        data, urls = scrape_grants()

        column_names = ['Opportunity Number', 'Opportunity Title', 'Agency', 'Opportunity Status', 'Posted Date', 'Close Date']

        # Create DataFrame
        df = pd.DataFrame(data, columns=column_names)

        # Ensure URLs are the same length as the table data
        df = df.iloc[:len(urls)]  # Adjust the DataFrame to the size of the URLs list, if necessary
        df['url'] = urls
        print(df)

        data = df.to_dict(orient="records")
        self.save(data)

    def save(self, data):
        collection = self.db["grants"]
        
        # Add today's date to each data entry
        date = datetime.now()
        for item in data:
            item['date'] = date

        print('Uploading data...')
        # Create unique index based on 'Opportunity Number'
        collection.create_index([('Opportunity Number', 1)], unique=True)

        try:
            collection.insert_many(data, ordered=False)  # Insert all records
            print("Data saved to MongoDB")
        except Exception as e:
            print(f"Error inserting data: {e}")
            print("Duplicates found, skipping those records.")
        
    def stop(self):
        print("Scraping Grants stopped...")
