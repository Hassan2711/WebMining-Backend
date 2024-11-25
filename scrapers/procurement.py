from .base import BaseScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
import os

# Get Selenium Remote WebDriver URL from environment
REMOTE_DRIVER = os.getenv('REMOTE_DRIVER', 'https://selenium-hub-production-352b.up.railway.app/wd/hub')


def extract_project_details(html_string):
    """Extract project details from HTML."""
    print("Extracting project details...")
    soup = BeautifulSoup(html_string, 'html.parser')
    print("Parsed HTML successfully.")
    projects = []

    for row in soup.find_all('div', class_='rt-tr-group'):
        print("Processing a row...")
        project = {}
        cells = row.find_all('div', class_='rt-td')
        if len(cells) >= 5:  # Ensure there are enough cells in the row
            project['title'] = cells[0].text.strip()
            project['organization'] = cells[1].text.strip()
            project['state'] = cells[2].text.strip()
            project['release_date'] = cells[3].text.strip()
            project['due_date'] = cells[4].text.strip()
            projects.append(project)
        else:
            print("Row skipped due to insufficient cells.")

    print(f"Extracted {len(projects)} projects.")
    return projects


def scrape_procurement():
    """Scrape procurement data."""
    print("Function Scraping Procurement started...")
    remote_address = REMOTE_DRIVER

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        command_executor=remote_address,
        options=options
    )
    print("Driver started")

    try:
        # Navigate to the login page
        driver.get("https://procurement.opengov.com/login")
        time.sleep(3)
        print("Navigated to the login page")

        # Enter email and password
        email = "jruff@bdrt.net"
        password = "hd5EAKy4xo30ksqbKyB4"
        email_field = driver.find_element(By.XPATH, "//input[@id='form-group-email']")
        email_field.send_keys(email)
        time.sleep(1)
        email_field.send_keys(Keys.ENTER)
        time.sleep(3)
        print("Email entered")

        password_field = driver.find_element(By.XPATH, "//input[@id='form-group-password']")
        password_field.send_keys(password)
        time.sleep(1)
        password_field.send_keys(Keys.ENTER)
        time.sleep(5)
        print("Password entered")

        driver.get("https://procurement.opengov.com/vendors/206554/open-bids")
        time.sleep(5)
        print("Navigated to the procurement page")

        try:
            total_pages_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[@class='-totalPages']"))
            )
            totalPages = int(total_pages_element.text)
            print(f"Total pages: {totalPages}")
        except TimeoutException:
            print("Timeout waiting for total pages element.")
            totalPages = 0

        data_list = []
        current_page = 1

        while current_page <= totalPages:
            print(f"Scraping page {current_page}...")

            # Extract table content
            table_element = driver.find_element(By.XPATH, '//*[@id="skip"]/div[3]/div/div/div[2]')
            table_html = table_element.get_attribute("outerHTML")
            projects = extract_project_details(table_html)
            data_list.extend(projects)

            # Check if "Next" button exists and is enabled
            try:
                next_button = driver.find_element(By.XPATH, "//button[normalize-space()='Next']")
                if next_button.is_enabled():
                    next_button.click()
                    current_page += 1
                    time.sleep(3)  # Allow time for the next page to load
                else:
                    print("Next button is disabled. Stopping pagination.")
                    break
            except NoSuchElementException:
                print("Next button not found. Stopping pagination.")
                break

        print(f"Scraped {len(data_list)} total projects.")
        return data_list

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Driver quit.")


class ProcurementScrape(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(name='procurement', **kwargs)

    def start(self):
        print("Scraping Procurement started...")
        data = scrape_procurement()
        print("Data extracted")
        print(data)

        # Ensure proper column names
        column_names = ['title', 'organization', 'state', 'release_date', 'due_date']
        if data:
            df = pd.DataFrame(data, columns=column_names)
        else:
            df = pd.DataFrame(columns=column_names)

        print("Dataframe created")
        print(df)

        data = df.to_dict(orient="records")
        print("Data converted to dictionary")
        print(data)
        self.save(data)

    def save(self, data):
        collection = self.db["grants"]
        date = datetime.now()

        # Filter out documents with missing or null 'title'
        filtered_data = [item for item in data if item.get('title') and item['title'].strip()]

        for item in filtered_data:
            item['date'] = date

        print("Uploading data...")
        collection.create_index([('title', 1)], unique=True)

        try:
            collection.insert_many(filtered_data, ordered=False)
        except Exception as e:
            print("Duplicates found or insertion failed:", str(e))
        print("Data saved to MongoDB")

    def stop(self):
        print("Scraping Procurement stopped.")
