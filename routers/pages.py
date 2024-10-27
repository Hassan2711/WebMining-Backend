from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()


# Pages

@router.get("/")
def read_root():
    # send file
    return FileResponse("pages/index.html")


@router.get("/yellowpages")
def read_yellowpages():
    # send file
    return FileResponse("pages/yellowpages.html")


@router.get("/grants")
def read_grants_gov():
    # send file
    return FileResponse("pages/grants.html")
