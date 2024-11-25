from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from passlib.context import CryptContext
from pymongo import MongoClient
from shared import get_db
from datetime import datetime

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = get_db()
users_collection = db["users"]
checkedby_collection = db["checkedby"]
downloadedby_collection = db["downloadedby"]

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/create_user/")
def create_user(user: UserCreate):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(user.password)
    user_data = {
        "username": user.username,
        "password": hashed_password,
        "role": user.role
    }
    result = users_collection.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return {"message": "User created successfully", "user": user_data}

class UserLogin(BaseModel):
    username: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    return users_collection.find_one({"username": username})

@router.post("/token")
def login(user: UserLogin):
    db_user = get_user(user.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    password_valid = verify_password(user.password, db_user["password"])
    if not password_valid:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    return {"access_token": f"fake-jwt-token-for-{user.username}", "token_type": "bearer"}

# New endpoint to get user information from token
@router.get("/users/me/")
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    # Extract username from the fake token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = authorization.split(" ")[1]
    if not token.startswith("fake-jwt-token-for-"):
        raise HTTPException(status_code=401, detail="Invalid token")

    username = token.replace("fake-jwt-token-for-", "")
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Return user details without password
    return {
        "name": user["username"],
        "role": user["role"]
    }

    
class CheckedByModel(BaseModel):
        yellowpages: str = ""
        procurement: str = ""
        grants_gov: str = ""
        article_factory: str = ""

# Add or update a checkedby entry
@router.put("/checkedby/start")
def update_checkedby_field(field: str, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid format")

    # Extract the username from the token
    token = authorization.split(" ")[1]
    if not token.startswith("fake-jwt-token-for-"):
        raise HTTPException(status_code=401, detail="Invalid token")

    username = token.replace("fake-jwt-token-for-", "")

    # Ensure the field is one of the expected values
    if field not in ["yellowpages", "procurement", "grants_gov", "article_factory"]:
        raise HTTPException(status_code=400, detail="Invalid field name")

    # Update the specified field with the username
    result = checkedby_collection.update_one({}, {"$set": {field: username}}, upsert=True)

    if result.modified_count > 0:
        return {"message": f"{field} checked by {username}"}
    else:
        return {"message": f"New {field} entry created by {username}"}
    
@router.get("/checkedby")
def get_checkedby():    
    # Retrieve the checkedby document for the user
    checkedby_data = checkedby_collection.find_one({})

    if not checkedby_data:
        raise HTTPException(status_code=404, detail="Checked by data not found")

    # Return the checkedby fields
    return {
        "yellowpages": checkedby_data.get("yellowpages", ""),
        "procurement": checkedby_data.get("procurement", ""),
        "grants_gov": checkedby_data.get("grants_gov", ""),
        "article_factory": checkedby_data.get("article_factory", "")
    }

    

class DownloadModel(BaseModel):
    yellowpages: str = ""
    yellowpages_time: str = ""
    procurement: str = ""
    procurement_time: str = ""
    grants_gov: str = ""
    grants_gov_time: str = ""
    article_factory: str = ""
    article_factory_time: str = ""

@router.put("/download/start")
def update_download_field(field: str, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid format")

    # Extract the username from the token
    token = authorization.split(" ")[1]
    if not token.startswith("fake-jwt-token-for-"):
        raise HTTPException(status_code=401, detail="Invalid token")

    username = token.replace("fake-jwt-token-for-", "")

    # Ensure the field is one of the expected values
    if field not in ["yellowpages", "procurement", "grants_gov", "article_factory"]:
        raise HTTPException(status_code=400, detail="Invalid field name")

    # Get the current time and date
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update the specified field with the username and timestamp
    result = downloadedby_collection.update_one(
        {},
        {"$set": {field: username, f"{field}_time": current_time}},
        upsert=True
    )

    if result.modified_count > 0:
        return {"message": f"{field} downloaded by {username} at {current_time}"}
    else:
        return {"message": f"New {field} entry created by {username} at {current_time}"}

@router.get("/downloadedby")
def get_downloadedby():
    # Retrieve the downloadedby document
    downloadedby_data = downloadedby_collection.find_one({})

    if not downloadedby_data:
        raise HTTPException(status_code=404, detail="Downloaded by data not found")

    # Return the downloadedby fields and timestamps
    return {
        "yellowpages": downloadedby_data.get("yellowpages", ""),
        "yellowpages_time": downloadedby_data.get("yellowpages_time", ""),
        "procurement": downloadedby_data.get("procurement", ""),
        "procurement_time": downloadedby_data.get("procurement_time", ""),
        "grants_gov": downloadedby_data.get("grants_gov", ""),
        "grants_gov_time": downloadedby_data.get("grants_gov_time", ""),
        "article_factory": downloadedby_data.get("article_factory", ""),
        "article_factory_time": downloadedby_data.get("article_factory_time", "")
    }