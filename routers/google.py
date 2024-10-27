from fastapi import APIRouter, Depends
from shared import get_db, get_tasker

tag = "Google Jobs"
router = APIRouter()


# @router.get("/scraper/google_jobs_demo", tags=["demo"])
# def get_google_jobs_demo():
#     data_list = []
#     all_data = get_google_jobs()
#     for data in all_data:
#         data_list.append([
#             data.get('title'),
#             data.get('company'),
#             data.get('location'),
#             data.get('date'),
#             data.get('url'),
#             data.get('status'),
#         ])
#         # print(data.get('name'))
#     # print()
#     return data_list


@router.get("/scraper/google_jobs/paginate", tags=["google_jobs"])
def get_google_jobs_paginate(db=Depends(get_db), page: int = 1, limit: int = 10):
    collection = db["google_jobs"]
    total_count = collection.count_documents({})
    total_pages = (total_count + limit - 1) // limit
    all_data = list(collection.find({}).sort("_id", -1).skip((page - 1) * limit).limit(limit))
    data_list = []
    for data in all_data:
        title = data.get('title')
        company = data.get('company')
        location = data.get('location')
        via = data.get('via')
        extensions = data.get('extensions')
        data_list.append({
            'title': title,
            'company': company,
            'location': location,
            'via': via,
            'extensions': extensions,
            'status': data.get('status'),
        })
    return {
        "data": data_list,
        "total_pages": total_pages
    }

@router.get("/scraper/google_jobs/start", tags=["google_jobs"])
def start_google_jobs(tasker=Depends(get_tasker)):
    tasker.start("google_jobs")
    return tasker.get_status()


@router.get("/scraper/google_jobs/status", tags=["google_jobs"])
def get_google_jobs_status(tasker=Depends(get_tasker)):
    return tasker.get_status()

@router.get("/scraper/google_jobs/complete", tags=["google_jobs"])
def complete_google_jobs(tasker=Depends(get_tasker)):
    if tasker.scrape_name == "google_jobs":
        return {
            "status": "google_jobs scraper is in progress"
        }

    if tasker.available:
        return {
            "status": "no task in progress"
        }
    else:
        return {
            "status": "task is in progress"
        }

@router.get("/scraper/google_jobs/data", tags=["google_jobs"])
def get_google_jobs_data(db=Depends(get_db)):
    collection = db["google_jobs"]
    all_data = list(collection.find({}))
    data_list = []
    for data in all_data:
        data_list.append({
            "title": data.get('title'),
            "company": data.get('company'),
            "location": data.get('location'),
            "date": data.get('date'),
            "url": data.get('url'),
            "status": data.get('status'),
        })
    return data_list


@router.get("/scraper/google_jobs/stop", tags=["google_jobs"])
def stop_google_jobs(tasker=Depends(get_tasker)):
    tasker.stop()
    return tasker.get_status()


@router.get("/scraper/google_jobs/clean", tags=["google_jobs"])
def clean_google_jobs(db=Depends(get_db)):
    collection = db["google_jobs"]
    collection.delete_many({})
    return {"status": "cleaned"}
