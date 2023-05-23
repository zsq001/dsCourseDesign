from fastapi import FastAPI, Request
from router import users
from router import courses
from router import enrollments

app = FastAPI()

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

