from fastapi import APIRouter, Depends, HTTPException, status
from database import SessionLocal

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from models import UserSchema, Users
from security import hash_password, verify_password

from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from config import settings
from sqlalchemy.exc import IntegrityError

class AuthorizationSchema(BaseModel):
    username: str
    password: str


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

async def get_db():
    async with SessionLocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

oauth2_dependency = Annotated[str, Depends(oauth2_scheme)]

async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(auth: oauth2_dependency, db: db_dependency):
    try:
        decoded_jwt = jwt.decode(auth, settings.secret_key, algorithms=[settings.algorithm])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate user", headers={"WWW-Authenticate": "Bearer"})

    username = decoded_jwt.get("sub")
    if username is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = await db.execute(select(Users).where(Users.username == username))
    user = user.scalar_one_or_none()
    return user


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(payload: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):

    user = await db.execute(select(Users).where(Users.username == payload.username))
    user = user.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Authorization Failed")
    
    jwt_token = await create_access_token(data={"sub": payload.username})

    return {"access_token": jwt_token,
            "token_type": "bearer"}



@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserSchema):
    new_user = Users(
        username = user_request.username,
        email = user_request.email,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        hashed_password = hash_password(user_request.password),
        role = "user"
    )
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="User with this username/email already exists")
    return {"message": "User created"}