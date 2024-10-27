from fastapi import APIRouter, Depends
from shared import get_db, get_tasker

tag = "Grants Gov"
router = APIRouter()


# Grants Gov

@router.get("/scraper/grants_gov", tags=["demo"])
def get_grants_gov(db=Depends(get_db)):
    collection = db["grants"]
    all_data = list(collection.find({}))
    data_list = []
    for data in all_data:
        data_list.append({
            "Opportunity Number": data.get('Opportunity Number'),
            "Opportunity Title": data.get('Opportunity Title'),
            "Agency": data.get('Agency'),
            "Opportunity Status": data.get('Opportunity Status'),
            "Posted Date": data.get('Posted Date'),
            "Close Date": data.get('Close Date'),
            "url": data.get('url'),
            # "status": data.get('status'),
        })
        # print(data.get('name'))
    # print()
    return data_list


@router.get("/scraper/grants_gov_demo", tags=["demo"])
def get_grants_gov_demo(db=Depends(get_db), tasker=Depends(get_tasker)):
    data_list = []
    all_data = get_grants_gov(db=db)
    for data in all_data:
        data_list.append([
            data.get('name'),
            data.get('agency'),
            data.get('category'),
            data.get('status'),
        ])
        # print(data.get('name'))
    # print()
    return data_list


@router.get("/scraper/grants_gov/paginate", tags=[tag])
def get_grants_gov_paginate(db=Depends(get_db), tasker=Depends(get_tasker), page: int = 1, limit: int = 10):
    collection = db["grants"]
    total_count = collection.count_documents({})
    total_pages = (total_count + limit - 1) // limit
    all_data = list(collection.find({}).sort(
        "_id", -1).skip((page - 1) * limit).limit(limit))
    data_list = []
    for data in all_data:
        data_list.append({
            "Opportunity Number": data.get('Opportunity Number'),
            "Opportunity Title": data.get('Opportunity Title'),
            "Opportunity Status": data.get('Opportunity Status'),
            "Posted Date": data.get('Posted Date'),
            "Close Date": data.get('Close Date'),
            "url": data.get('url'),
            "status": data.get('status'),
        })
    return {
        "data": data_list,
        "total_pages": total_pages
    }


@router.get("/scraper/grants_gov/start", tags=[tag])
def start_grants_gov(db=Depends(get_db), tasker=Depends(get_tasker)):
    tasker.start("grants")
    return tasker.get_status()


@router.get("/scraper/grants_gov/status", tags=[tag])
def get_grants_gov_status(db=Depends(get_db), tasker=Depends(get_tasker)):
    return tasker.get_status()


@router.get("/scraper/grants_gov/complete", tags=[tag])
def complete_grants_gov(db=Depends(get_db), tasker=Depends(get_tasker)):
    if tasker.scrape_name == "grants":
        return {
            "status": "grants scraper is in progress"
        }

    if tasker.available:
        return {
            "status": "no task in progress"
        }
    else:
        return {
            "status": "task is in progress"
        }


@router.get("/scraper/grants_gov/data", tags=[tag])
def get_grants_gov_data(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["grants"]
    all_data = list(collection.find({}))
    data_list = []
    for data in all_data:
        data_list.append({
            "Opportunity Number": data.get('Opportunity Number'),
            "Opportunity Title": data.get('Opportunity Title'),
            "Opportunity Status": data.get('Opportunity Status'),
            "Posted Date": data.get('Posted Date'),
            "Close Date": data.get('Close Date'),
            "url": data.get('url'),
            "status": None,
        })
    return data_list


@router.get("/scraper/grants_gov/stop", tags=[tag])
def stop_grants_gov(db=Depends(get_db), tasker=Depends(get_tasker)):
    tasker.stop()
    return tasker.get_status()


@router.get("/scraper/grants_gov/clean", tags=[tag])
def clean_grants_gov(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["grants"]
    collection.delete_many({})
    return {"status": "cleaned"}


@router.get("/scraper/grants_gov/send", tags=[tag])
def sent_grants_gov(db=Depends(get_db), tasker=Depends(get_tasker)):
    collection = db["grants"]
    all_data = list(collection.find({}))
    data_list = []
    count = 0
    for data in all_data:
        data_list.append({
            "Name": data.get('Opportunity Title'),
            "Opportunity Number": data.get('Opportunity Number'),
            "Agency": data.get('Agency'),
            "Opportunity Status": data.get('Opportunity Status'),
            "Posted Date": data.get('Posted Date'),
            "Close Date": data.get('Close Date'),
            "url": data.get('url'),
        })
        if count == 30:
            break
    tasker.sent_to_airtable('grants', data_list)

    # print(data_list)
