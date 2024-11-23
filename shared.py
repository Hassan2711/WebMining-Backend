from pymongo import MongoClient
from scraping_task import ScrapingTask
import os

MONGODB_URL = os.environ.get('MONGODB_URL')
if not MONGODB_URL:
    raise ValueError("MONGODB_URL is not set!")
print(f"MONGODB_URL: {MONGODB_URL}")

# connect to the mongo database
client = MongoClient(MONGODB_URL)
assert client is not None, "Could not connect to the database"
client.server_info()
print("Connected to the database")

db = client["mydatabase"]
tasker = ScrapingTask(database=db)

def get_db():
    return db

def get_tasker():
    return tasker
