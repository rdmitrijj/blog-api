from pydantic import BaseModel
from database import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey
from datetime import datetime, timezone
from sqlalchemy import DateTime, UniqueConstraint

from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

class UserSchema(BaseModel):

    username: str
    email: str
    first_name: str
    last_name: str
    password: str


class Blogs(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                                                 onupdate=lambda: datetime.now(timezone.utc))

class Likes(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        # to make sure thst user can like one time
        UniqueConstraint("blog_id", "user_id", name="uix_user_blog_like"),
    )

class Comments(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id"), nullable=False)
    content: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
