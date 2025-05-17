from fastapi import FastAPI, HTTPException
from jose import jwt
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from .schema import UserRegister, UserLogin
import httpx
import os

app = FastAPI()

db_url = "http://localhost"
db_port = 8000

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register", status_code=201)
async def register(user: UserRegister):
    async with httpx.AsyncClient() as client:
        hashed_pw = bcrypt.hash(user.password)
        user_data = {
            "username": user.username,
            "email": user.email,
            "password": hashed_pw,
            "role": "player"
        }
        response = await client.post(f"{db_url}:{db_port}/users/", json=user_data)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=response.text)
        return {"msg": "User registered"}

@app.post("/login")
async def login(user: UserLogin):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{db_url}:{db_port}/users/{user.username}/password")
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="User not found")
        user_data = response.json()
        hashed_pw = user_data.get("password")
        print(f"Hashed password from DB: {hashed_pw}")
        print(f"Password from request: {user.password}")
        if not hashed_pw or not bcrypt.verify(user.password, hashed_pw):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        role = user_data.get("role", "player")
        token = create_access_token(
            data={"sub": user.username, "role": role},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": token, "token_type": "bearer"}
