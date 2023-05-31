from fastapi import FastAPI, Request
from router import users, courses, enrollments, schedule
from fastapi.responses import FileResponse
import logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(schedule.router)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"], )

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
