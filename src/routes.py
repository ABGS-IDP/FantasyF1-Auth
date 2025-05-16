from fastapi import FastAPI, HTTPException
from jose import jwt
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from models import UserRegister, UserLogin

app = FastAPI()

fake_users_db = {}

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
def register(user: UserRegister):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username exists")
    hashed_pw = bcrypt.hash(user.password)
    fake_users_db[user.username] = hashed_pw
    return {"msg": "User registered"}

@app.post("/login")
def login(user: UserLogin):
    hashed_pw = fake_users_db.get(user.username)
    if not hashed_pw or not bcrypt.verify(user.password, hashed_pw):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}
