from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Users, Blogs
from .auth import get_current_user
from security import verify_password, hash_password
from argon2.exceptions import InvalidHashError


router = APIRouter(
    prefix="/account",
    tags=["account"]
)

async def get_db():
    async with SessionLocal() as session:
        yield session

class UserResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    class Config:
        from_attributes = True

class UserToChange(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str

class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str

class BlogCreate(BaseModel):
    title: str
    content: str

class UpdateSchema(BaseModel):
    title: str
    content: str

db_dependency = Annotated[AsyncSession, Depends(get_db)]

user_dependency = Annotated[Users, Depends(get_current_user)]

@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_my_user(user: user_dependency):
    return user

@router.get("/me/blogs", status_code=status.HTTP_200_OK)
async def get_my_blogs(user: user_dependency, db: db_dependency):

    blogs = await db.execute(select(Blogs).where(Blogs.author_id == user.id))
    blogs = blogs.scalars().all()
    return blogs

@router.put("/me", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_user(user: user_dependency, payload: UserToChange, db: db_dependency):

    user.username = payload.username
    user.email = payload.email
    user.first_name = payload.first_name
    user.last_name = payload.last_name

    await db.commit()

@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(user: user_dependency, payload: UserPasswordChange, db: db_dependency):
    
    if not verify_password(payload.old_password, user.hashed_password):
         raise HTTPException(status_code=403, detail="Passwords do not match") 
    
    user.hashed_password = hash_password(payload.new_password)

    await db.commit()

@router.post("/me/createblog", status_code=status.HTTP_201_CREATED)
async def create_my_blog(user: user_dependency, payload: BlogCreate, db: db_dependency):

    new_blog = Blogs(
        author_id = user.id,
        title = payload.title,
        content = payload.content
    )

    db.add(new_blog)
    await db.commit()
    await db.refresh(new_blog)
    return {"message": "Blog created successfully", "blog_id": new_blog.id}

@router.put("/me/blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_blog(blog_id: int, payload: UpdateSchema, user: user_dependency, db: db_dependency,):
    
    result = await db.execute(select(Blogs).where(Blogs.id == blog_id, Blogs.author_id == user.id))

    blog = result.scalar_one_or_none()
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    blog.title = payload.title
    blog.content = payload.content

    await db.commit()


@router.delete("/me/blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_blog(blog_id: int, user: user_dependency, db: db_dependency):

    blog = await db.execute(select(Blogs).where(Blogs.id == blog_id, Blogs.author_id == user.id))
    blog = blog.scalar_one_or_none()
    if blog is None:
        raise HTTPException(status_code=404, detail="Not Found")
    await db.delete(blog)
    await db.commit()
