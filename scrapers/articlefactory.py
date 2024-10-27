from .base import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime
import requests, re
import pandas as pd

TOTAL_PAGES = 1

# Function to get the last page number
def get_last_page_number(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the HTML content
        html_content = response.text
        
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all page number links
        page_links = soup.find('div', class_='pagination').find_all('a', class_='number__button')
        
        # Extract the page numbers
        page_numbers = [int(link.text) for link in page_links]
        
        # Get the maximum page number
        last_page_number = max(page_numbers)
        
        return last_page_number
    else:
        print("Failed to retrieve the content. Status code:", response.status_code)
        return None


def extract_article_urls(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the div with class 'article__list'
        article_list_div = soup.find('div', class_='article__list')
        
        # Initialize a list to store extracted URLs
        urls = []
        
        # Find all anchor tags within the div
        if article_list_div:
            for anchor in article_list_div.find_all('a'):
                # Extract the URL from the 'href' attribute
                article_url = anchor.get('href')
                # Append the URL to the list
                urls.append(article_url)
        
        return urls
    else:
        # If the request was not successful, print an error message
        print(f"Failed to fetch URL: {url}")
        return []


def fetch_article_details(url):
    response = requests.get('https://www.articlesfactory.com'+url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print(url)
        # Extracting the title
        title = soup.find('div', class_='title').get_text(strip=True) if soup.find('div', class_='title') else 'N/A'
        
        # Extracting the date and formatting it
        date = soup.find('div', class_='date').get_text(strip=True) if soup.find('div', class_='date') else 'N/A'
        
        # Extracting the author
        author = soup.find('a', class_='profile').get_text(strip=True) if soup.find('a', class_='profile') else 'N/A'
        
        # Extracting the media image URL
        media_image = soup.find('div', class_='media').find('img')['src'] if soup.find('div', class_='media') and soup.find('div', class_='media').find('img') else 'N/A'
        
        # Extracting tags and categories
        tags_container = soup.find('div', class_='tags')
        tags = []
        categories = []
        
        if tags_container:
            tags_elems = tags_container.find_all('a', class_='el__tag')
            for tag in tags_elems:
                if "/tag/" in tag['href']:  # This checks if the href contains "/tag/" to identify it as a tag
                    tags.append(tag.get_text(strip=True))
                elif "/articles/" in tag['href']:  # This checks for categories similarly
                    categories.append(tag.get_text(strip=True))
        
        # Extracting and formatting article content
        article_content = soup.find('div', class_='article__desc').get_text(separator='\n', strip=True) if soup.find('div', class_='article__desc') else 'N/A'
        # print(date)
        # # Parse the string into a datetime object
        # if ' ' in date:
        #     datetime_obj = datetime.strptime(date.replace(author, ''), "%b %d%H:%M%Y") # Feb 2106:592024
        # else:
        #     datetime_obj = datetime.strptime(date.replace(author, ''), "%b%d%H:%M%Y")
        # # Format the datetime object as per your requirements
        # formatted_datetime = datetime_obj.strftime("%b %d, %Y %I:%M %p")
        
        # Find the 4th occurrence of "\n"
        desired_newline_index = article_content.find("\n", 0, article_content.count("\n", 0, len(article_content)-1))
        for i in range(5):
            desired_newline_index = article_content.find("\n", desired_newline_index + 1)

        # Find the starting position of the article_content after the 4th newline
        start_index = desired_newline_index + 1

        # Find the ending position before "\nArticle "tagged" as:"
        end_index = article_content.find("\nArticle ", start_index)

        if start_index != -1 and end_index != -1:
            # Extract the desired article_content
            desired_text = article_content[start_index:end_index]
            # print(desired_text)
        else:
            print("Couldn't find the desired article_content.")


        return {
            'title': title,
            'date_time': date.replace(author, ''), #formatted_datetime,
            'author': author,
            'media_image': media_image,
            'tags': (", ".join(tags)).title(),  # Joining list items into a single string
            'categories': ", ".join(categories).title(),  # Same for categories
            'article_content': desired_text,
            'article_url': url
        }
    else:
        print(f"Failed to fetch article: {url}")
        return None




def scrape_articlefactory():
    #### Extracting Last Page Number ####

    # URL of the page
    url = 'https://www.articlesfactory.com/tag/pet-care/page1.html'

    # Get the last page number
    last_page_number = get_last_page_number(url)

    if last_page_number is not None:
        print("Last Page Number:", last_page_number)

    #### Extracting Article URLs ####

    # Base URL of the webpage
    base_url = 'https://www.articlesfactory.com/tag/pet-care/page{}.html'

    # Initialize a list to store all article URLs
    all_article_urls = []

    # Set the last page number
    last_page_number = TOTAL_PAGES

    # Iterate over each page to extract article URLs
    for page_number in range(1, last_page_number + 1):
        page_url = base_url.format(page_number)
        article_urls = extract_article_urls(page_url)
        all_article_urls.extend(article_urls)

    # Print the extracted URLs
    for idx, article_url in enumerate(all_article_urls, start=1):
        print(f"Article {idx}: {article_url}")
    
    #### Extracting Article Details ####

    articles_data = []

    for url in all_article_urls:
        article_details = fetch_article_details(url)
        if article_details:  # Checking if details were found
            articles_data.append(article_details)

    # Creating DataFrame
    df_articles = pd.DataFrame(articles_data)

    # print(df_articles)
    print('Total articles extracted:', len(df_articles))
    
    return articles_data



class ArticleFactoryScrape(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(name='article_factory', **kwargs)
        
    def start(self):
        print("Scraping Article Factory started...")
        data = scrape_articlefactory()
        
        columns = ['title', 'date_time', 'author', 'media_image', 'tags', 'categories', 'article_content', 'article_url']

        # Create DataFrame
        df = pd.DataFrame(data, columns=columns)
        data = df.to_dict(orient="records")
        
        self.save(data)

    def save(self, data):
        collection = self.db["article_factory"]
        # add today's date to the data
        date = datetime.now()
        for item in data:
            item['date'] = date
        print('uploading data')
        # avoid duplicates
        collection.create_index([('name', 1)], unique=True)
        try: 
            collection.insert_many(data, ordered=False)
        except Exception as e:
            print("Duplicated found!")
        print("Data saved successfully.")
        
    def stop(self):
        print("Scraping Article Factory stopped.")
