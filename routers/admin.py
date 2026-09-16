from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from models import Users, Blogs
from .auth import get_current_user
from sqlalchemy import select
from pydantic import BaseModel

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

async def get_db():
    async with SessionLocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]

user_dependency = Annotated[Users, Depends(get_current_user)]

class UpdateSchema(BaseModel):
    title: str
    content: str

@router.put("/blogs/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_blog(item_id: int, user: user_dependency, db: db_dependency, payload: UpdateSchema):

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    blog = await db.execute(select(Blogs).where(Blogs.id == item_id))
    blog = blog.scalar_one_or_none()
    if blog is None:
        raise HTTPException(status_code=404, detail="Not Found")
    blog.title = payload.title
    blog.content = payload.content
    await db.commit()

@router.delete("/blogs/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(item_id: int, user: user_dependency, db: db_dependency):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    blog = await db.execute(select(Blogs).where(Blogs.id == item_id))
    blog = blog.scalar_one_or_none()
    if blog is None:
        raise HTTPException(status_code=404, detail="Not Found")
    await db.delete(blog)
    await db.commit()