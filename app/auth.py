from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db_models import SessionLocal, User as DBUser

app = FastAPI()

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "61313c0afff56df25a032b86a2aef63f82439e32eff06c11649fb568c7e732f5")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str
    role: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
    db_user_username = get_user(db, user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already exists")
        
    db_user_email = db.query(DBUser).filter(DBUser.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already exists")
        
    hashed_password = pwd_context.hash(user.password)
    new_user = DBUser(username=user.username, email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({
        "sub": str(user.username),
        "email": str(user.email),
        "role": user.role
    })
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if not isinstance(username, str) or username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if not isinstance(role, str) or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user(db, username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return User(username=username, email=user.email, role=role)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Role-based permission example
@app.get("/admin")
def admin_endpoint(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    role = payload.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return {"msg": "Welcome, admin!"}
