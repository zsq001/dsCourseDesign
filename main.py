from fastapi import FastAPI, Request, HTTPException
from router import users, courses, enrollments, schedule, maps, activities
from fastapi.responses import FileResponse
import logging
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(schedule.router)
app.include_router(maps.router)
app.include_router(activities.router)

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


class TimeSimulator:
    def __init__(self):
        self.current_week = 1
        self.current_day = 1
        self.current_hour = 0

    def simulate_forward(self):
        self.current_hour = (self.current_hour + 1) % 24

        # 判断是否到达新的一天
        if self.current_hour == 0:
            self.current_day += 1

            # 判断是否到达新的一周
            if self.current_day == 8:
                self.current_week += 1
                self.current_day = 1

    def set_time(self, week: int, day: int, hour: int):
        if not self._is_valid_time(week, day, hour):
            raise HTTPException(status_code=400, detail="无效的时间")

        self.current_week = week
        self.current_day = day
        self.current_hour = hour

    def _is_valid_time(self, week: int, day: int, hour: int) -> bool:
        # 在此处添加验证时间的逻辑，例如判断周数、日期和小时数的范围是否合法
        return True


# 创建时间模拟器实例
time_simulator = TimeSimulator()


@app.get("/log_download")
async def log():
    return FileResponse('app.log', filename='log.txt', media_type='application/octet-stream')


@app.get("/simulate_forward")
def simulate_forward():
    time_simulator.simulate_forward()
    return {
        "current_week": time_simulator.current_week,
        "current_day": time_simulator.current_day,
        "current_hour": time_simulator.current_hour
    }


@app.get("/current_time")
def get_current_time():
    return {
        "current_week": time_simulator.current_week,
        "current_day": time_simulator.current_day,
        "current_hour": time_simulator.current_hour
    }


class Time(BaseModel):
    week: int
    day: int
    hour: int


@app.put("/set_time")
def set_time(time: Time):
    try:
        time_simulator.set_time(time.week, time.day, time.hour)
        return {"message": "success"}
    except HTTPException as e:
        raise e
