from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from passlib.context import CryptContext
from pymongo import MongoClient
from shared import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = get_db()
users_collection = db["users"]
checkedby_collection = db["checkedby"]

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
    grants: str = ""
    articles: str = ""

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
    if field not in ["yellowpages", "procurement", "grants", "articles"]:
        raise HTTPException(status_code=400, detail="Invalid field name")

    # Update the specified field with the username
    result = checkedby_collection.update_one({}, {"$set": {field: username}}, upsert=True)

    if result.modified_count > 0:
        return {"message": f"{field} checked by {username}"}
    else:
        return {"message": f"New {field} entry created by {username}"}