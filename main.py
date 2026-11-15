import os
from functools import lru_cache
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_USER_AUTHENTICATION")

from Auth_funcs.crud_auth import (
    Base,
    check_login,
    check_user_exists,
    regis_user,
)


class UserDatas(BaseModel):
    user_name: str
    user_password: str
    user_email: str


class LoginData(BaseModel):
    user_name: str
    user_password: str


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv("BACKEND_CORS_ORIGINS")
    if configured_origins:
        return [
            origin.strip()
            for origin in configured_origins.split(",")
            if origin.strip()
        ]
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


app = FastAPI(title="Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_engine():
    database_url = os.getenv("DATABASE_USER_AUTHENTICATION")
    if not database_url:
        raise RuntimeError("Set the DATABASE_USER_AUTHENTICATION environment variable")
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_db() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


@app.get("/")
def check_run():
    return {"message": "Backend Running..."}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserDatas, session: Session = Depends(get_db)):
    if check_user_exists(session, user.user_name, user.user_email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists.",
        )
    regis_user(session, user.user_name, user.user_password, user.user_email)
    return {"message": "User registered successfully."}


@app.post("/login")
def login_user(user: LoginData, session: Session = Depends(get_db)):
    if not check_login(session, user.user_name, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    return {"message": "User logged in successfully."}


#===========================
# Terminal database testing
#===========================
act = input("Enter 'run' to start the FastAPI server or 'test' to run terminal tests: ")
if act == "run":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
else:
    from terminal_tester import terminal_db_tester
    with Session(get_engine()) as session:
        terminal_db_tester(session)
