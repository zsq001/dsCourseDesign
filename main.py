from fastapi import FastAPI, Request
from router import users, courses, enrollments, schedule
from fastapi.responses import FileResponse
import logging

app = FastAPI()

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(schedule.router)

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("daily")


@app.get("/log_download")
async def log():
    return FileResponse('app.log', filename='log.txt', media_type='application/octet-stream')
