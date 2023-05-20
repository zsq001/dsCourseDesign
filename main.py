from fastapi import FastAPI, HTTPException
from router import users
from router import courses
from router import enrollments


app = FastAPI()

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):

    return {"message": f"Hello {name}"}
