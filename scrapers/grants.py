from .base import BaseScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import pandas as pd
import time
import logging
import os
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Selenium Remote WebDriver URL from environment
REMOTE_DRIVER_URL = os.getenv("REMOTE_DRIVER_URL", "https://selenium-hub-production-352b.up.railway.app/wd/hub")


def is_grid_accessible():
    """Check if the Selenium Grid is accessible."""
    try:
        response = requests.get(f"{REMOTE_DRIVER_URL}/status", timeout=10)
        if response.status_code == 200 and response.json().get("value", {}).get("ready"):
            logger.info("Selenium Grid is ready.")
            return True
        else:
            logger.error(f"Selenium Grid not ready: {response.json()}")
    except Exception as e:
        logger.error(f"Error accessing Selenium Grid: {e}")
    return False


def init_webdriver():
    """Initialize the Selenium WebDriver using the remote Selenium Grid."""
    if not is_grid_accessible():
        raise Exception("Selenium Grid is not accessible.")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    retries = 3
    delay = 5  # seconds

    for attempt in range(retries):
        try:
            driver = webdriver.Remote(
                command_executor=REMOTE_DRIVER_URL,
                options=options
            )
            logger.info("Remote WebDriver initialized successfully.")
            return driver
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"WebDriver initialization failed, retrying... ({attempt + 1}/{retries})")
                time.sleep(delay)
            else:
                logger.error(f"Failed to initialize WebDriver after {retries} attempts: {e}")
                raise


def scrape_grants():
    """Scrape grants data from the website."""
    logger.info("Starting grants scraping...")
    driver = init_webdriver()
    table_data = []
    filtered_urls = []

    try:
        url = "https://www.grants.gov/search-grants"
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logger.info(f"Loaded URL: {url}")

        page_count = 0

        while True:
            page_count += 1
            logger.info(f"Scraping page {page_count}...")

            try:
                # Scroll to the bottom to ensure all data is loaded
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.END)
                time.sleep(2)

                # Extract table data
                table_element = driver.find_element(By.XPATH, "//*[@id='__nuxt']/div[4]/div/div/div/div[2]/div[3]/table")
                page_data = []

                # Extract links
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/search-results-detail/" in href:
                        filtered_urls.append(href)

                for row in table_element.find_elements(By.TAG_NAME, "tr"):
                    row_data = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
                    page_data.append(row_data)

                # Exclude header and footer rows
                filtered_list = page_data[2:-1]
                logger.info(f"Extracted {len(filtered_list)} rows from page {page_count}.")
                table_data.extend(filtered_list)

                # Check for next button
                next_button = driver.find_elements(By.XPATH, "//span[@class='usa-pagination__link-text'][normalize-space()='Next']")
                if next_button:
                    next_button[0].click()
                    time.sleep(2)
                else:
                    logger.info("No more pages to scrape.")
                    break

            except TimeoutException:
                logger.error(f"Timeout while scraping page {page_count}.")
                break

        logger.info(f"Scraped {page_count} pages with {len(table_data)} rows of data.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        driver.quit()
        logger.info("WebDriver quit successfully.")
        return table_data, filtered_urls


class GrantsScrape(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(name='grants', **kwargs)

    def start(self):
        logger.info("Starting grants scraping task...")
        data, urls = scrape_grants()

        column_names = ['Opportunity Number', 'Opportunity Title', 'Agency', 'Opportunity Status', 'Posted Date', 'Close Date']
        df = pd.DataFrame(data, columns=column_names)

        # Ensure URLs are the same length as the table data
        df = df.iloc[:len(urls)]
        df['url'] = urls
        logger.info(f"DataFrame created successfully with {len(df)} rows.")
        logger.info(df.head())

        # Convert DataFrame to a dictionary for MongoDB
        data = df.to_dict(orient="records")
        self.save(data)

    def save(self, data):
        collection = self.db["grants"]
        date = datetime.now()

        for item in data:
            item['date'] = date
            collection.update_one(
                {'Opportunity Number': item['Opportunity Number']},
                {'$set': item},
                upsert=True
            )
        logger.info("Data saved to MongoDB successfully with upserts.")

    def stop(self):
        logger.info("Grants scraping task stopped.")
