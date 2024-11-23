from fastapi import APIRouter, Depends
from shared import get_db, get_tasker
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd

tag = "Article Factory"
router = APIRouter()


# article factory

@router.get("/scraper/article_factory", tags=["demo"])
def get_article_factory(db=Depends(get_db)):
    collection = db["article_factory"]
    all_data = list(collection.find({}))
    data_list = []
    for data in all_data:
        # columns
        # ['title', 'date_time', 'author', 'media_image', 'tags', 'categories', 'article_content', 'article_url']
        data_list.append({
            "title": data.get('title'),
            "date_time": data.get('date_time'),
            "author": data.get('author'),
            "media_image": data.get('media_image'),
            "tags": data.get('tags'),
            "categories": data.get('categories'),
            "article_content": data.get('article_content'),
            "article_url": data.get('article_url'),
            "status": data.get('status'),
        })
        # print(data.get('name'))
    # print()
    return data_list

@router.get("/scraper/article_factory_demo", tags=["demo"])
def get_article_factory_demo(db=Depends(get_db)):
    data_list = []
    all_data = get_article_factory()
    for data in all_data:
        data_list.append([
            data.get('title'),
            data.get('date_time'),
            data.get('author'),
            data.get('media_image'),
            data.get('tags'),
            data.get('categories'),
            data.get('article_content'),
            data.get('article_url'),
            data.get('status'),
        ])
        # print(data.get('name'))
    # print()
    return data_list

@router.get("/scraper/article_factory/paginate", tags=[tag])
def get_article_factory_paginate(db=Depends(get_db), page: int = 1, limit: int = 10):
    collection = db["article_factory"]
    total_count = collection.count_documents({})
    total_pages = (total_count + limit - 1) // limit
    all_data = list(collection.find({}).sort("_id", -1).skip((page - 1) * limit).limit(limit))
    data_list = []
    for data in all_data:
        data_list.append({
            "title": data.get('title'),
            "date_time": data.get('date_time'),
            "author": data.get('author'),
            "media_image": data.get('media_image'),
            "tags": data.get('tags'),
            "categories": data.get('categories'),
            "article_content": data.get('article_content'),
            "article_url": data.get('article_url'),
            "status": data.get('status'),
        })
    return {
        "data": data_list,
        "total_pages": total_pages
    }

@router.get("/scraper/article_factory/start", tags=[tag])
def start_article_factory(tasker=Depends(get_tasker)):
    tasker.start("article_factory")
    return tasker.get_status()

@router.get("/scraper/article_factory/status", tags=[tag])
def get_article_factory_status(tasker=Depends(get_tasker)):
    return tasker.get_status()

@router.get("/scraper/article_factory/complete", tags=[tag])
def complete_article_factory(tasker=Depends(get_tasker)):
    if tasker.scrape_name == "article_factory":
        return {
            "status": "article_factory scraper is in progress"
        }

    if tasker.available:
        return {
            "status": "no task in progress"
        }
    else:
        return {
            "status": "task is in progress"
        }
    
@router.get("/scraper/article_factory/data", tags=[tag])
def get_article_factory_data(db=Depends(get_db)):
    collection = db["article_factory"]
    all_data = list(collection.find({}))
    data_list = []
    for data in all_data:
        data_list.append({
            "title": data.get('title'),
            "date_time": data.get('date_time'),
            "author": data.get('author'),
            "media_image": data.get('media_image'),
            "tags": data.get('tags'),
            "categories": data.get('categories'),
            "article_content": data.get('article_content'),
            "article_url": data.get('article_url'),
            "status": data.get('status'),
        })
    return data_list


@router.get("/scraper/article_factory/stop", tags=[tag])
def stop_article_factory(tasker=Depends(get_tasker)):
    tasker.stop()
    return tasker.get_status()


@router.get("/scraper/article_factory/clean", tags=[tag])
def clean_article_factory(db=Depends(get_db)):
    collection = db["article_factory"]
    collection.delete_many({})
    return {"status": "cleaned"}


@router.get("/scraper/article_factory/send", tags=[tag])
def sent_article_factory(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["article_factory"]
    all_data = list(collection.find({"status": {"$ne": "sent"}}))
    data_list = []
    count = 0
    for data in all_data:
        data_list.append({
            "Name": data.get('title'),
            "date_time": data.get('date_time'),
            "author": data.get('author'),
            "media_image": data.get('media_image'),
            "tags": data.get('tags'),
            "categories": data.get('categories'),
            "article_content": data.get('article_content'),
            "article_url": data.get('article_url'),
        })
        count += 1
        if count == 10:
            break
        
    # tasker.sent_to_airtable('article_factory', data_list)
    
    # print(data_list)

@router.get("/scraper/article_factory/download", tags=[tag])
def download_article_factory_data(db=Depends(get_db)):
    # Fetch data from the "article_factory" MongoDB collection
    collection = db["article_factory"]
    data = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB's internal `_id`

    if not data:
        return {"error": "No data available for Article Factory."}

    # Convert data to a Pandas DataFrame
    df = pd.DataFrame(data)

    # Create an in-memory CSV file
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    # Return the CSV as a streaming response
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=article_factory_data.csv"},
    )
