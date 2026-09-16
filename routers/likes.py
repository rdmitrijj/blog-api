
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import get_current_user
from models import Users, Blogs, Likes, Comments
from database import SessionLocal
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

router = APIRouter(
    prefix="/blogs/like",
    tags=["likes"]
)


async def get_db():
    async with SessionLocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]

user_dependency = Annotated[Users, Depends(get_current_user)]


@router.post("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def to_like_a_blog(item_id: int, db: db_dependency, user: user_dependency):

    like_result = await db.execute(select(Likes).where(Likes.blog_id == item_id, Likes.user_id == user.id))
    like_data = like_result.scalar_one_or_none()
    like_data = Likes(
        blog_id = item_id,
        user_id = user.id
    )
    try:
        db.add(like_data)
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=403, detail="You have already liked this post")

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def to_delete_a_like(item_id: int, db: db_dependency, user: user_dependency):

    like_data = await db.execute(select(Likes).where(Likes.blog_id == item_id, Likes.user_id == user.id))
    like_data = like_data.scalar_one_or_none()
    if like_data is None:
        raise HTTPException(status_code=404, detail="Not Found")
    await db.delete(like_data)
    await db.commit()