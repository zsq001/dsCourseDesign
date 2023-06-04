from fastapi import FastAPI, Request, HTTPException
from datetime import datetime, timedelta
import util
from router import users, courses, enrollments, schedule, maps, activities
from fastapi.responses import FileResponse
import logging
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import router.courses, router.enrollments

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

week = ["","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

alarms = []

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


class Alarm(BaseModel):
    id: int = None
    note: str
    time: str
    frequency: str
    user: str = None
    day: str = None
    week: str = None

def get_max_id():
    max_id = 0
    for alarm in alarms:
        if alarm.id > max_id:
            max_id = alarm.id
    return max_id

@app.put("/set_time")
def set_time(time: Time):
    try:
        time_simulator.set_time(time.week, time.day, time.hour)
        return {"message": "success"}
    except HTTPException as e:
        raise e


def course_alarm(user):

    courses = router.courses.Course.from_json("courses.json")
    enrollments = router.enrollments.Enrollment.from_json("enrollments.json")
    course_list = []
    for enrollment in enrollments:
        if enrollment.id == user:
            course_list = enrollment.course_id
    today = week[get_current_day_of_week()]
    alarm_list = []
    for course in courses:
        if course.id in course_list:
            for schedule in course.class_schedule:
                print(schedule)
                if schedule[0] == today:
                    alarm_list.append(course)
    if len(alarm_list) == 0:
        return
    return alarm_list


@app.get("/alarms/")
def get_alarms(request: Request):
    user = util.getUser(request)
    alarm_list = []
    for alarm in alarms:
        if alarm.user == user:
            alarm_list.append(alarm)
    return alarm_list

@app.post("/alarms/")
def create_alarm(request: Request, alarm: Alarm):
    user = util.getUser(request)
    alarm.id = get_max_id() + 1
    alarm.user = user
    alarm.day = time_simulator.current_day
    alarm.week = time_simulator.current_week
    alarms.append(alarm)
    return alarm

@app.get("/alarms/{alarm_id}")
def get_alarm(request: Request, alarm_id: int):
    for alarm in alarms:
        if alarm.id == alarm_id and alarm.user == util.getUser(request):
            return alarm
    return {"message": "Alarm not found"}

@app.delete("/alarms/{alarm_id}")
def delete_alarm(request: Request, alarm_id: int):
    for alarm in alarms:
        if alarm.id == alarm_id and alarm.user == util.getUser(request):
            alarms.remove(alarm)
            return {"message": "Alarm deleted"}
    return {"message": "Alarm not found"}


@app.get("/course_today")
def course_today(request: Request): #get today's course from courses.json
    user = util.getUser(request)
    notice = []
    notice.append(course_alarm(user))
    return notice


@app.get("/ring/")
def check_alarms(request: Request):
    ringing_alarms = []
    time = str(time_simulator.current_hour)
    for alarm in alarms:
        print(alarm)
        print(get_current_day_of_week())
        print(time)
        if alarm.user == util.getUser(request) and alarm.time == time and alarm.frequency == "single" \
                and alarm.day == get_current_day_of_week() and alarm.week == time_simulator.current_week:
            ringing_alarms.append(alarm)
        elif alarm.user == util.getUser(request) and alarm.time == time and alarm.frequency == "daily":
            ringing_alarms.append(alarm)
        elif alarm.user == util.getUser(request) and alarm.time == time and alarm.frequency == "weekly" \
                and alarm.day == get_current_day_of_week():
            ringing_alarms.append(alarm)
    return ringing_alarms


def get_current_day_of_week():
    current_day = time_simulator.current_day
    return current_day % 7

