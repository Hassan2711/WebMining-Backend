from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from shared import get_db, get_tasker

tag = "Stats"
router = APIRouter()

@router.get("/daily_localwork", tags=[tag])
def daily_localwork(db=Depends(get_db), tasker=Depends(get_tasker)):
    return JSONResponse(content={"data": 50})

@router.get("/daily_batrips", tags=[tag])
def daily_batrips(db=Depends(get_db), tasker=Depends(get_tasker)):
    return JSONResponse(content={"data": 100})

# weekly
@router.get("/weekly_localwork", tags=[tag])
def weekly_localwork(db=Depends(get_db), tasker=Depends(get_tasker)):
    return JSONResponse(content={"data": 300})

@router.get("/weekly_batrips", tags=[tag])
def weekly_batrips(db=Depends(get_db), tasker=Depends(get_tasker)):
    return JSONResponse(content={"data": 600})

# monthly

@router.get("/monthly_localwork", tags=[tag])
def monthly_localwork(db=Depends(get_db), tasker=Depends(get_tasker)):
    return JSONResponse(content={"data": 1500})

@router.get("/monthly_batrips", tags=[tag])
def monthly_batrips(db=Depends(get_db), tasker=Depends(get_tasker)):
    return JSONResponse(content={"data": 3000})

# yearly

@router.get("/yearly_localwork", tags=[tag])
def yearly_localwork(db=Depends(get_db), tasker=Depends(get_tasker)):
    return JSONResponse(content={"data": 6000})

@router.get("/yearly_batrips", tags=[tag])
def yearly_batrips(db=Depends(get_db), tasker=Depends(get_tasker)):
    return JSONResponse(content={"data": 12000})
