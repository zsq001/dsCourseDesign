from fastapi import APIRouter, Cookie, HTTPException, Response, Body
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
import json

class Payload(BaseModel):
    name: str = ""

router = APIRouter(prefix="/courses", tags=["courses"])

COURSES_FILE = 'courses.json'
ENROLLMENTS_FILE = 'enrollments.json'

def read_json(filename: str) -> str:
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def write_json(data: dict, filename: str) -> None:
    with open(filename, 'w') as f:
        json.dump(data, f)


class Course:
    def __init__(self, id, name, class_schedule):
        self.id = id
        self.name = name
        self.class_schedule = class_schedule

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'class_schedule': [
                {
                    'day_of_week': day_of_week,
                    'class_periods': class_periods
                }
                for day_of_week, class_periods in self.class_schedule
            ]
            #'class_schedule': self.class_schedule
        }

    @classmethod
    def from_json(cls, json_file):
        with open(json_file) as f:
            data = json.load(f)

        courses = []
        for course_data in data['courses']:
            id = course_data['id']
            name = course_data['name']
            class_schedule = []

            for schedule in course_data['class_schedule']:
                day_of_week = schedule['day_of_week']
                class_periods = schedule['class_periods']
                class_schedule.append((day_of_week, class_periods))

            courses.append(cls(id, name, class_schedule))

        return courses


@router.get("/{course_id}")
async def get_courses(course_id: int):
    courses = Course.from_json('courses.json')
    course_id = course_id - 1
    course_dict = courses[course_id].to_dict()
    json_string = json.dumps(course_dict, separators=(',', ':'), ensure_ascii=False)
    print(json_string)
    return Response(content=json_string.replace('\\', ''), media_type='application/json')

@router.post("/{course_id}/update_name")  #[{"day_of_week":"1","class_periods":[2,3,4]},{"day_of_week":"4","class_periods":[5,6,7]}]
async def update_courses(course_id: int, name: str = Body(...)):
    courses = Course.from_json('courses.json')
    course_id = course_id - 1
    print(name)
    courses[course_id].name = name
    print(courses[course_id].name)
    write_json({'courses': [course.to_dict() for course in courses]}, COURSES_FILE)
    return Response(content='{"status": "success"}', media_type='application/json')

@router.post("/{course_id}/update_schedule")
async def update_courses_schedule(course_id: int, class_schedule_tmp: List[Dict[str, Any]]):
    courses = Course.from_json('courses.json')
    course_id = course_id - 1
    courses[course_id].class_schedule = []
    for classes in class_schedule_tmp:
        courses[course_id].class_schedule.append((classes['day_of_week'], classes['class_periods']))

    # courses[course_id].class_schedule = [classes['day_of_week'], classes['class_periods'] for classes in class_schedule_tmp]
    #courses[course_id].class_schedule =
    write_json({'courses': [course.to_dict() for course in courses]}, COURSES_FILE)
    return Response(content='{"status": "success"}', media_type='application/json')
