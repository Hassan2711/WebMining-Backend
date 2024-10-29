from fastapi import APIRouter, Depends
from shared import get_db, get_tasker
from pydantic import BaseModel


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
            data.get('status'),
        ])
        # print(data.get('name'))
    # print()
    return data_list


# paginate 
@router.get("/scraper/yellowpages/paginate", tags=[tag])
def get_yellowpages_paginate(db=Depends(get_db), page: int = 1, limit: int = 10):
    collection = db["yellowpages"]
    total_count = collection.count_documents({})
    total_pages = (total_count + limit - 1) // limit
    all_data = list(collection.find({}).sort("_id", -1).skip((page - 1) * limit).limit(limit))
    data_list = []
    for data in all_data:
        data_list.append({
            "name": data.get('Name'),
            "address": data.get('Address'),
            "phone": data.get('Phone'),
            "link": data.get('Link'),
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
    tasker.sent_to_airtable('yellowpages', data_list)
    