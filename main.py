from fastapi import FastAPI
from routers import account, auth, blogs, comments, likes, admin



app = FastAPI()

app.include_router(account.router)

app.include_router(auth.router)

app.include_router(blogs.router)

app.include_router(comments.router)

app.include_router(likes.router)

app.include_router(admin.router)