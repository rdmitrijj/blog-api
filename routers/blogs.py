
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import get_current_user
from models import Users, Blogs, Likes, Comments
from database import SessionLocal
from sqlalchemy import select, func, distinct
from pydantic import BaseModel
from datetime import datetime


router = APIRouter(
    prefix="/blogs",
    tags=["blogs"]
)

async def get_db():
    async with SessionLocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]

user_dependency = Annotated[Users, Depends(get_current_user)]


class BlogListResponse(BaseModel):
    id: int
    title: str
    author_id: int
    created_at: datetime
    likes: int
    comments: int

class CommentResponse(BaseModel): 
    id: int
    user_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}

class OneBlogResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    likes: int
    comments: list[CommentResponse]

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[BlogListResponse])
async def get_blogs(db: db_dependency):
     
    all_blogs = await db.execute(select(Blogs.id, Blogs.title, Blogs.author_id, Blogs.created_at, func.count(distinct(Likes.id)).label("likes"), func.count(distinct(Comments.id)).label("comments"))
                                 .join(Likes, Blogs.id == Likes.blog_id, isouter=True)
                                 .join(Comments, Blogs.id == Comments.blog_id, isouter=True)
                                 .group_by(Blogs.id))

    all_blogs = all_blogs.all()
    return all_blogs

@router.get("/{item_id}", status_code=status.HTTP_200_OK)
async def get_blog(item_id: int, db: db_dependency):


    blog_result = await db.execute(select(Blogs).where(Blogs.id == item_id))
    blog = blog_result.scalar_one_or_none()

    if blog is None:
        raise HTTPException(status_code=404, detail="Not Found")
    comments_result = await db.execute(select(Comments).where(Comments.blog_id == item_id))
    comments = comments_result.scalars().all()
    comments = [CommentResponse.model_validate(c) for c in comments]

    likes_result = await db.execute(select(func.count(Likes.id)).where(Likes.blog_id == item_id))
    likes = likes_result.scalar_one_or_none()


    result = OneBlogResponse(
        id = blog.id,
        title = blog.title,
        content = blog.content,
        author_id = blog.author_id,
        created_at = blog.created_at,
        likes = likes,
        comments = comments
    )
    return result


