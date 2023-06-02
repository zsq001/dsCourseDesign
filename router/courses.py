from fastapi import APIRouter, HTTPException, Request, Response, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import util
import logging

logger = logging.getLogger("daily")


class Payload(BaseModel):
    name: str = ""
    required: bool = False
    class_schedule: List[Dict[str, Any]] = []
    exam_time: str = ""
    exam_place: str = ""
    class_place: str = ""
    single: bool = False


router = APIRouter(prefix="/courses", tags=["courses"])

COURSES_FILE = 'courses.json'


def read_json(filename: str) -> str:
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def write_json(data: dict, filename: str) -> None:
    with open(filename, 'w') as f:
        json.dump(data, f)


def checkAdmin(request: Request):
    user = request.cookies.get("user")
    print(user)
    if user != "0":
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return user


class class_schedule(BaseModel):
    day_of_week: str = ""
    class_periods: List[int] = []


class Update(BaseModel):
    course_id: int
    type_id: int
    value: str = None
    class_schedule_tmp: List[Dict[str, Any]] = None


class Course:
    def __init__(self, id, name, required, class_schedule, exam_time, exam_place, class_place, single):
        self.id = id
        self.name = name
        self.required = required
        self.class_schedule = class_schedule
        self.exam_time = exam_time
        self.exam_place = exam_place
        self.class_place = class_place
        self.single = single

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'required': self.required,
            'class_schedule': [
                {
                    'day_of_week': day_of_week,
                    'class_periods': class_periods
                }
                for day_of_week, class_periods in self.class_schedule
            ],
            'exam_time': self.exam_time,
            'exam_place': self.exam_place,
            'class_place': self.class_place,
            'single': self.single
        }

    @classmethod
    def from_json(cls, json_file):
        with open(json_file) as f:
            data = json.load(f)

        courses = []
        for course_data in data['courses']:
            id = course_data['id']
            name = course_data['name']
            required = course_data['required']
            exam_time = course_data['exam_time']
            exam_place = course_data['exam_place']
            class_place = course_data['class_place']
            single = course_data['single']
            class_schedule = []

            for schedule in course_data['class_schedule']:
                day_of_week = schedule['day_of_week']
                class_periods = schedule['class_periods']
                class_schedule.append((day_of_week, class_periods))

            courses.append(cls(id, name, required, class_schedule, exam_time, exam_place, class_place, single))

        return courses


@router.get("/{course_id}")
async def get_courses(request: Request, course_id: int):
    user = util.getUser(request)
    courses = Course.from_json(COURSES_FILE)
    course_id = course_id - 1
    course_dict = courses[course_id].to_dict()
    json_string = json.dumps(course_dict, separators=(',', ':'), ensure_ascii=False)
    return Response(content=json_string.replace('\\', ''), media_type='application/json')


@router.put("/update/")
async def update(request: Request, update_req: Update):
    checkAdmin(request)
    courses = Course.from_json(COURSES_FILE)
    course_id = update_req.course_id - 1
    course_id_str = str(course_id)
    if update_req.type_id == 1:
        courses[course_id].name = update_req.value

        logger.info('Updated class ' + course_id_str + ' name to ' + update_req.value)
    elif update_req.type_id == 2:
        courses[course_id].required = update_req.value
        logger.info('Updated class ' + course_id_str + ' required to ' + update_req.value)
    elif update_req.type_id == 3:
        courses[course_id].class_schedule = []
        for schedule in update_req.class_schedule_tmp:
            day_of_week = schedule['day_of_week']
            class_periods = schedule['class_periods']
            courses[course_id].class_schedule.append((day_of_week, class_periods))
        logger.info('Updated class ' + course_id_str + ' class_schedule ')
    elif update_req.type_id == 4:
        courses[course_id].exam_time = update_req.value
        logger.info('Updated class ' + course_id_str + ' exam time to ' + update_req.value)
    elif update_req.type_id == 5:
        courses[course_id].exam_place = update_req.value
        logger.info('Updated class ' + course_id_str + ' exam place to ' + update_req.value)
    elif update_req.type_id == 6:
        courses[course_id].class_place = update_req.value
        logger.info('Updated class ' + course_id_str + ' class place to ' + update_req.value)
    write_json({'courses': [course.to_dict() for course in courses]}, COURSES_FILE)
    return Response(content='{"status": "success"}', media_type='application/json')


@router.post("/add_course")
async def add_course(request: Request, payload: Payload):
    checkAdmin(request)
    courses = Course.from_json(COURSES_FILE)
    courses.append(Course(len(courses) + 1, payload.name, payload.required, [], payload.exam_time, payload.exam_place,
                          payload.class_place, payload.single))
    for classes in payload.class_schedule:
        courses[len(courses) - 1].class_schedule.append((classes['day_of_week'], classes['class_periods']))
    write_json({'courses': [course.to_dict() for course in courses]}, COURSES_FILE)
    return Response(content='{"status": "success"}', media_type='application/json')


@router.post("/delete_course/{course_id}")
async def delete_course(request: Request, course_id: int):
    checkAdmin(request)
    courses = Course.from_json(COURSES_FILE)
    course_id = course_id - 1
    courses.pop(course_id)
    for i in range(len(courses)):
        courses[i].id = i + 1
    write_json({'courses': [course.to_dict() for course in courses]}, COURSES_FILE)
    return Response(content='{"status": "success"}', media_type='application/json')
