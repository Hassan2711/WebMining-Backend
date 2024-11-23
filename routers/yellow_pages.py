from fastapi import APIRouter, Depends, Query
from shared import get_db, get_tasker
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd


tag = "Yellow Pages"
router = APIRouter()


# Yellow Pages
@router.get("/scraper/yellowpages", tags=["demo"])
def get_yellowpages(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["yellowpages"]
    all_data = list(collection.find({}).sort("_id", -1))
    data_list = []
    for data in all_data:
        data_list.append({
            "name": data.get('Name'),
            "address": data.get('Address'),
            "phone": data.get('Phone'),
            "link": data.get('Link'),
            "status": data.get('status'),
        })
        # print(data.get('name'))
    # print()
    return data_list


@router.get("/scraper/yellowpages_demo", tags=["demo"])
def get_yellowpages_demo(db=Depends(get_db), tasker=Depends(get_tasker)):
    # collection = db["yellowpages"]
    # all_data = list(collection.find({}))
    data_list = []
    all_data = get_yellowpages()
    for data in all_data:
        data_list.append([
            data.get('name'),
            data.get('address'),
            data.get('phone'),
            data.get('link'),
            data.get('email'),
            data.get('regular_hours'),
            data.get('claimed'),
            data.get('general_info'),
            data.get('services_products'),
            data.get('neighborhoods'),
            data.get('amenities'),
            data.get('languages'),
            data.get('aka'),
            data.get('social_links'),
            data.get('categories'),
            data.get('photos_url'),
            data.get('other_info'),
            data.get('other_links'),
            data.get('status'),
        ])
        # print(data.get('name'))
    # print()
    return data_list

# paginate 
@router.get("/scraper/yellowpages/paginate", tags=[tag])
def get_yellowpages_paginate(
    db=Depends(get_db), 
    page: int = 1, 
    limit: int = 10, 
    filterBy: str = Query("null")
):
    collection = db["yellowpages"]
    
    # Apply the filter based on `filterBy` value
    query = {}
    if filterBy == "Approved":
        query["status"] = "Approved"
    elif filterBy == "Rejected":
        query["status"] = "Rejected"

    # Use the `query` dictionary in `count_documents` and `find`
    total_count = collection.count_documents(query)
    total_pages = (total_count + limit - 1) // limit

    # Apply filtering, pagination, and sorting
    all_data = list(
        collection.find(query)
        .sort("_id", -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    
    data_list = []
    for data in all_data:
        data_list.append({
            "name": data.get('Name'),
            "address": data.get('Address'),
            "phone": data.get('Phone'),
            "link": data.get('Link'),
            "email": data.get('email'),
            "regular_hours": data.get('regular_hours'),
            "claimed": data.get('claimed'),
            "general_info": data.get('general_info'),
            "services_products": data.get('services_products'),
            "neighborhoods": data.get('neighborhoods'),
            "amenities": data.get('amenities'),
            "languages": data.get('languages'),
            "aka": data.get('aka'),
            "social_links": data.get('social_links'),
            "categories": data.get('categories'),
            "photos_url": data.get('photos_url'),
            "other_info": data.get('other_info'),
            "other_links": data.get('other_links'),
            "status": data.get('status'),
        })
    
    return {
        "data": data_list,
        "total_pages": total_pages
    }


# Global dictionary to store settings
settings_cache = {
    "state": None,
    "category": None
}

class YellowPagesSettings(BaseModel):
    state: str
    category: str

@router.post("/scraper/yellowpages/start", tags=["yellowpages"])
async def set_yellowpages_settings(settings: YellowPagesSettings, db=Depends(get_db), tasker=Depends(get_tasker)):
    try:
        # Update the global dictionary with new settings
        settings_cache["state"] = settings.state
        settings_cache["category"] = settings.category
        print(settings.state)
        print(settings.category)
        
        return
    except Exception as e:
        print(e)

@router.get("/scraper/yellowpages/start", tags=[tag])
def start_yellowpages(db=Depends(get_db), tasker=Depends(get_tasker)):
    state = settings_cache.get("state")
    category = settings_cache.get("category")
    print(state)
    print(category)

    tasker.start("yellowpages", state=state, category=category)
    return tasker.get_status()


@router.get("/scraper/yellowpages/status", tags=[tag])
def get_yellowpages_status(db=Depends(get_db), tasker=Depends(get_tasker)):
    return tasker.get_status()


@router.get("/scraper/yellowpages/complete", tags=[tag])
def complete_yellowpages(db=Depends(get_db), tasker=Depends(get_tasker)):
    if tasker.scrape_name == "yellowpages":
        return {
            "status": "yellow_pages scraper is in progress"
        }

    if tasker.available:
        return {
            "status": "no task in progress"
        }
    else:
        return {
            "status": "task is in progress"
        }


@router.get("/scraper/yellowpages/data", tags=[tag])
def get_yellowpages_data(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["yellowpages"]
    all_data = list(collection.find({}))
    data_list = []
    for data in all_data:
        data_list.append({
            "name": data.get('Name'),
            "address": data.get('Address'),
            "phone": data.get('Phone'),
            "link": data.get('Link'),
            "status": data.get('status'),
        })
    return data_list


@router.get("/scraper/yellowpages/clean", tags=[tag])
def clean_yellowpages(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["yellowpages"]
    collection.delete_many({})
    return {"status": "cleaned"}


@router.get("/scraper/yellowpages/send", tags=[tag])
def send_yellowpages(db=Depends(get_db), tasker=Depends(get_tasker)):
    # get the data status is not "sent"
    collection = db["yellowpages"]
    all_data = list(collection.find({"status": {"$ne": "sent"}}))
    data_list = []
    count = 0
    # send this data to airtable
    for data in all_data:
        data_list.append({
            "Name": data.get('Name'),
            "Address": data.get('Address'),
            "Phone": data.get('Phone'),
            "Link": data.get('Link'),
        })
        count += 1
        if count == 10:
            break
    print(data_list)
    
    # change the status to "sent"
    # for data in all_data:
    #     collection.update_one(
    #         {"_id": data.get('_id')},
    #         {"$set": {"status": "sent"}}
    #     )
    # tasker.sent_to_airtable('yellowpages', data_list)
    
@router.get("/scraper/yellowpages/download", tags=[tag])
def download_yellowpages_data(db=Depends(get_db)):
    # Fetch all data from the "yellowpages" MongoDB collection
    collection = db["yellowpages"]
    data = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB's internal `_id` field

    if not data:
        return {"error": "No data available for Yellow Pages."}

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
        headers={"Content-Disposition": "attachment; filename=yellowpages_data.csv"},
    )
