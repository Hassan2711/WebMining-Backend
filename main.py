from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from airtable import Airtable
from shared import get_db, get_tasker
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from scrapers.runner import Runner

from routers import (
    pages, 
    stats,
    yellow_pages,
    grants_gov, 
    procurement,
    article_factory,
    google,
    users
)

# create the FastAPI app
app = FastAPI()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(pages.router)
app.include_router(stats.router)
app.include_router(grants_gov.router, dependencies=[Depends(get_db), Depends(get_tasker)])
app.include_router(procurement.router, dependencies=[Depends(get_db), Depends(get_tasker)])
app.include_router(yellow_pages.router, dependencies=[Depends(get_db), Depends(get_tasker)])
app.include_router(article_factory.router, dependencies=[Depends(get_db), Depends(get_tasker)])
app.include_router(google.router, dependencies=[Depends(get_db), Depends(get_tasker)])
app.include_router(users.router, dependencies=[Depends(get_db), Depends(get_tasker)])

scheduler = BackgroundScheduler()

def job_function():
    print("Scheduled Task Started")
    db = get_db()
    runner = Runner(db=db)
    runner.run_grants()
    runner.run_yellow_pages()
    runner.run_article_factory()
    runner.run_google_jobs()
    runner.run_procurement()
    print("Scheduled Task Ended")

# scheduler.add_job(job_function, 'interval', seconds=5)
# Add the job to the scheduler
scheduler.add_job(job_function, CronTrigger(hour=0, minute=0, timezone='US/Pacific'))
scheduler.start()
