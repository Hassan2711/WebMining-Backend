from fastapi import APIRouter, Depends
from shared import get_db, get_tasker
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd

tag = "Procurement"
router = APIRouter()

# procurement

@router.get("/scraper/procurement", tags=["demo"])
def get_procurement(db=Depends(get_db)):
    collection = db["procurement"]
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
        # print(data.get('name'))
    # print()
    return data_list

@router.get("/scraper/procurement_demo", tags=["demo"])
def get_procurement_demo():
    data_list = []
    all_data = get_procurement()
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

@router.get("/scraper/procurement/paginate", tags=["procurement"])
def get_procurement_paginate(db=Depends(get_db), page: int = 1, limit: int = 10):
    collection = db["procurement"]
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

@router.get("/scraper/procurement/start", tags=["procurement"])
def start_procurement(db=Depends(get_db), tasker=Depends(get_tasker)):
    tasker.start("procurement")
    return tasker.get_status()

@router.get("/scraper/procurement/status", tags=["procurement"])
def get_procurement_status(db=Depends(get_db), tasker=Depends(get_tasker)):
    return tasker.get_status()

@router.get("/scraper/procurement/complete", tags=["procurement"])
def complete_procurement(db=Depends(get_db), tasker=Depends(get_tasker)):
    if tasker.scrape_name == "procurement":
        return {
            "status": "procurement scraper is in progress"
        }

    if tasker.available:
        return {
            "status": "no task in progress"
        }
    else:
        return {
            "status": "task is in progress"
        }
        
@router.get("/scraper/procurement/data", tags=["procurement"])
def get_procurement_data(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["procurement"]
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

@router.get("/scraper/procurement/stop", tags=["procurement"])
def stop_procurement(db=Depends(get_db), tasker=Depends(get_tasker)):
    tasker.stop()
    return tasker.get_status()

@router.get("/scraper/procurement/sent", tags=["procurement"])
def sent_procurement(db=Depends(get_db), tasker=Depends(get_tasker)):
    tasker.sent('procurement')

@router.get("/scraper/procurement/clean", tags=["procurement"])
def clean_procurement(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["procurement"]
    collection.delete_many({})
    return {"status": "cleaned"}

@router.get("/scraper/procurement/send", tags=["procurement"])
def sent_procurement(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["procurement"]
    all_data = list(collection.find({"status": {"$ne": "sent"}}))
    data_list = []
    count = 0
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
        })
        count += 1
        if count == 10:
            break
        
    # tasker.sent_to_airtable('procurement', data_list)
    
    # print(data_list)
    
@router.get("/scraper/procurement/download", tags=["procurement"])
def download_procurement_data(db=Depends(get_db)):
    # Fetch all data from the "procurement" MongoDB collection
    collection = db["procurement"]
    data = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB's internal `_id` field

    if not data:
        return {"error": "No data available for Procurement."}

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
        headers={"Content-Disposition": "attachment; filename=procurement_data.csv"},
    )
