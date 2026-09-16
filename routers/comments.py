
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import get_current_user
from models import Users, Blogs, Likes, Comments
from database import SessionLocal
from sqlalchemy import select, func  
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/blogs/comment",
    tags=["comments"]
)


async def get_db():
    async with SessionLocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]

user_dependency = Annotated[Users, Depends(get_current_user)]

class CommentRequest(BaseModel):
    content: str

@router.post("/write/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def write_comment(item_id: int, user: user_dependency, db: db_dependency, payload: CommentRequest):

        blog = await db.execute(select(Blogs).where(Blogs.id == item_id))

        if blog.scalar_one_or_none() is None:
             raise HTTPException(status_code=404, detail="Not found")

        comment = Comments(
            blog_id = item_id,
            user_id = user.id,
            content = payload.content
        )
        db.add(comment)
        try:
            await db.commit()
        except IntegrityError:
             await db.rollback()
             raise HTTPException(status_code=409, detail="Could not create a comment")
@router.delete("/delete/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, user: user_dependency, db: db_dependency):


    comment_to_delete_result = await db.execute(select(Comments).where(Comments.id == comment_id, Comments.user_id == user.id))
    comment = comment_to_delete_result.scalar_one_or_none()
    if comment is None:
         raise HTTPException(status_code=404, detail="Not Found")
    await db.delete(comment)
    await db.commit()
