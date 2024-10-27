from .base import BaseScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
import os

# REMOTE_DRIVER = 'https://standalone-chrome-production-4a6a.up.railway.app'
REMOTE_DRIVER = os.getenv('REMOTE_DRIVER')


def extract_project_details(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    projects = []

    for row in soup.find_all('div', class_='rt-tr-group'):
        project = {}
        cells = row.find_all('div', class_='rt-td')
        if len(cells) >= 5:  # Check if there are enough cells
            # Extract details with error handling for links
            link_element = cells[0].find('a')
            if link_element:
                project['title'] = link_element.text.strip()
            else:
                project['title'] = cells[0].text.strip()

            project['organization'] = cells[1].text.strip()
            project['state'] = cells[2].text.strip()
            project['release_date'] = cells[3].text.strip()
            project['due_date'] = cells[4].text.strip()

            # for i in range(len(project['title'])):
            #     # Find the link by link text and click it
            # link = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.LINK_TEXT, "Privatization of Meter Services"))
            # )
            # link.click()
            # time.sleep(3)
            # # Get the current URL
            # current_url = driver.current_url
            # print(current_url)
            # project['current_url'] = current_url

            projects.append(project)

    return projects


def scrape_procurement():
    print("function Scraping Procurement started...")
    remote_address = REMOTE_DRIVER

    options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
        command_executor=remote_address,
        options=options
    )
    print("Driver started")
    
    try:
        # navigate to the login page
        driver.get("https://procurement.opengov.com/login")
        time.sleep(3)
        print("Navigated to the login page")

        # enter the email and password
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
        
        # 
        rows_per_page_element = driver.find_element(By.XPATH, "//select[@aria-label='rows per page']")
        rows_per_page_element.send_keys('100')
        totalPages = driver.find_element(By.XPATH, "//span[@class='-totalPages']").text
        
        print(totalPages)

        total_pages = 2
        totalPages = 2

        for i in range(len(int(totalPages))):
            page_input_element = driver.find_element(By.XPATH, "//input[@value='1']")
            rows_per_page_element.send_keys('100')

            table_element = driver.find_element_by_xpath('//*[@id="skip"]/div[3]/div/div/div[2]')  

            # Extract the HTML content of the table
            table_html = table_element.get_attribute("outerHTML")

            projects = extract_project_details(table_html)

            data_list = []

            for project in projects:
                data_list.append(project)
                print(project)
            
            # Check if the "Next" button is enabled and click it to move to the next page
            try:
                next_button = driver.find_element(By.XPATH, "//button[normalize-space()='Next']")
                if next_button.is_enabled():
                    next_button.click()
                    current_page += 1
                    # Wait for the next page to load (Optional: adjust as needed for your page)
                    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div[2]')))
                else:
                    break  # Exit loop if next button is not enabled
            except Exception as e:
                print("Error navigating to the next page:", str(e))
                break
            print(len(data_list))
            
            return data_list
        
        print("Total pages scraped:", current_page)
    except Exception as e:
        # print(f"url: {url}")
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Driver quit")


class ProcurementScrape(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(name='procurement', **kwargs)
        
    def start(self):
        print("Scraping Procurement started...")
        data = scrape_procurement()
        print("Data extracted")
        print(data)
        
        column_names = ['Opportunity Number', 'Opportunity Title', 'Agency', 'Opportunity Status', 'Posted Date', 'Close Date']

        # Create DataFrame
        df = pd.DataFrame(data, columns=column_names)
        print("Dataframe created")
        print(df)
        # df['url'] = urls 
        # TODO: check this 
        # df
        
        data = df.to_dict(orient="records")    
        print("Data converted to dictionary")
        print(data)
        self.save(data)
        
    def save(self, data):
        collection = self.db["grants"]
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
        print("Scraping Grants stopped...")
