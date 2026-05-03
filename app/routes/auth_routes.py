from fastapi import APIRouter
from app.database.db import read_db, write_db
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 🔹 Hash password (FIXED)
def hash_password(password):
    return pwd_context.hash(password[:72])  # 🔥 FIX


def verify_password(plain, hashed):
    return pwd_context.verify(plain[:72], hashed)


def create_token(username):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# 🔹 Signup
@router.post("/signup")
def signup(user: dict):
    db = read_db()

    for u in db["users"]:
        if u["username"] == user["username"]:
            return {"error": "User already exists"}

    user["password"] = hash_password(user["password"])
    db["users"].append(user)

    write_db(db)

    return {"message": "User created successfully"}


# 🔹 Login
@router.post("/login")
def login(user: dict):
    db = read_db()

    for u in db["users"]:
        if u["username"] == user["username"]:
            if verify_password(user["password"], u["password"]):
                token = create_token(user["username"])
                return {"token": token}

    return {"error": "Invalid credentials"}