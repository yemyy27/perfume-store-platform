from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime, timedelta
import uvicorn
import os
import jwt
import bcrypt

app = FastAPI(title="User Service", version="1.0.0")

# CORS configuration
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:8080,http://localhost:3000").split(",")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()
users_db = []

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(email: str):
    return next((u for u in users_db if u["email"] == email), None)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}

@app.post("/api/auth/register", response_model=User, status_code=201)
async def register(user: UserRegister):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": len(users_db) + 1,
        "email": user.email,
        "password": hash_password(user.password),
        "full_name": user.full_name,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    users_db.append(new_user)
    
    return {
        "id": new_user["id"],
        "email": new_user["email"],
        "full_name": new_user["full_name"],
        "created_at": new_user["created_at"],
        "is_active": new_user["is_active"]
    }

@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    user = get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=User)
async def get_me(current_user = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "created_at": current_user["created_at"],
        "is_active": current_user["is_active"]
    }

@app.get("/api/users")
async def list_users():
    return [{"id": u["id"], "email": u["email"], "full_name": u["full_name"], 
             "created_at": u["created_at"], "is_active": u["is_active"]} 
            for u in users_db]

@app.get("/")
async def root():
    return {"service": "User Service", "version": "1.0.0", "status": "running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
