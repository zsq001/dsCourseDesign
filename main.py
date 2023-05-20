from fastapi import FastAPI, HTTPException
from router import users
from router import courses


app = FastAPI()

app.include_router(users.router)
app.include_router(courses.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):

    return {"message": f"Hello {name}"}
