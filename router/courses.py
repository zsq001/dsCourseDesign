from fastapi import APIRouter, HTTPException, Request, Response, Body
from typing import List, Dict, Any
from pydantic import BaseModel
import json
import util


class Payload(BaseModel):
    name: str = ""
    required: bool = False
    class_schedule: List[Dict[str, Any]] = []


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
    if user != 'admin':
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return user


class Course:
    def __init__(self, id, name, required, class_schedule):
        self.id = id
        self.name = name
        self.required = required
        self.class_schedule = class_schedule

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
            ]
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
            class_schedule = []

            for schedule in course_data['class_schedule']:
                day_of_week = schedule['day_of_week']
                class_periods = schedule['class_periods']
                class_schedule.append((day_of_week, class_periods))

            courses.append(cls(id, name, required, class_schedule))

        return courses


@router.get("/{course_id}")
async def get_courses(request: Request, course_id: int):
    user = util.getUser(request)
    courses = Course.from_json(COURSES_FILE)
    course_id = course_id - 1
    course_dict = courses[course_id].to_dict()
    json_string = json.dumps(course_dict, separators=(',', ':'), ensure_ascii=False)
    return Response(content=json_string.replace('\\', ''), media_type='application/json')


@router.post("/{course_id}/update_name")
async def update_courses(request: Request, course_id: int, name: str = Body(...)):
    checkAdmin(request)
    courses = Course.from_json(COURSES_FILE)
    course_id = course_id - 1
    print(name)
    courses[course_id].name = name
    print(courses[course_id].name)
    write_json({'courses': [course.to_dict() for course in courses]}, COURSES_FILE)
    return Response(content='{"status": "success"}', media_type='application/json')


@router.post("/{course_id}/update_required")
async def update_courses_required(request: Request, course_id: int, required: bool = Body(...)):
    checkAdmin(request)
    courses = Course.from_json(COURSES_FILE)
    course_id = course_id - 1
    courses[course_id].required = required
    write_json({'courses': [course.to_dict() for course in courses]}, COURSES_FILE)
    return Response(content='{"status": "success"}', media_type='application/json')


@router.post("/{course_id}/update_schedule")
async def update_courses_schedule(request: Request, course_id: int, class_schedule_tmp: List[Dict[str, Any]]):
    checkAdmin(request)
    courses = Course.from_json(COURSES_FILE)
    course_id = course_id - 1
    courses[course_id].class_schedule = []
    for classes in class_schedule_tmp:
        courses[course_id].class_schedule.append((classes['day_of_week'], classes['class_periods']))
    write_json({'courses': [course.to_dict() for course in courses]}, COURSES_FILE)
    return Response(content='{"status": "success"}', media_type='application/json')


@router.post("/add_course")
async def add_course(request: Request, payload: Payload):
    checkAdmin(request)
    courses = Course.from_json(COURSES_FILE)
    courses.append(Course(len(courses) + 1, payload.name, payload.required, []))
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
