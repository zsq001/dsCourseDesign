from fastapi import APIRouter, HTTPException, Request
from typing import List
from pydantic import BaseModel
import util
import json
from .courses import Course

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

ENROLLMENTS_FILE = 'enrollments.json'
COURSES_FILE = 'courses.json'


def read_json(filename: str) -> str:
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def write_json(data: dict, filename: str) -> None:
    with open(filename, 'w') as f:
        json.dump(data, f)


class Enrollment:
    def __init__(self, id, course_id):
        self.id = id
        self.course_id = course_id

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id
        }

    @classmethod
    def from_json(cls, json_file):
        with open(json_file) as f:
            data = json.load(f)

        enrollments = []
        for enrollment_data in data['students']:
            id = enrollment_data['id']
            course_id = enrollment_data['course_id']
            enrollments.append(cls(id, course_id))

        return enrollments


@router.get("/")
async def get_enrollments(request: Request, student_id: int = None):
    user = util.getUser(request)
    print(user)
    if user == 0:
        user = student_id
    enrollments = Enrollment.from_json(ENROLLMENTS_FILE)
    for enrollment in enrollments:
        if enrollment.id == user:
            return enrollment.to_dict()


@router.post("/update_course")
async def update_course(request: Request, course_id: List[int], student_id: int = None):
    user = util.getUser(request)
    enrollments = Enrollment.from_json(ENROLLMENTS_FILE)
    if user == 0:
        user = student_id
    for enrollment in enrollments:
        if enrollment.id == user:
            enrollment.course_id = course_id
            write_json({'students': [enrollment.to_dict() for enrollment in enrollments]}, ENROLLMENTS_FILE)
            return enrollment.to_dict()

    raise HTTPException(status_code=404, detail="Student not found")


@router.get("/required_class")
async def required_class(request: Request, student_id: int = None):
    enrollments = Enrollment.from_json(ENROLLMENTS_FILE)
    user = util.getUser(request)
    tmp = []
    if user == 0:
        user = student_id
    for enrollment in enrollments:
        if enrollment.id == user:
            for courseid in enrollment.course_id:
                courses = Course.from_json(COURSES_FILE)
                courseid = courseid - 1
                if courses[courseid].required:
                    tmp.append(courses[courseid].id)
            return tmp

    raise HTTPException(status_code=404, detail="Student not found")


@router.get("/optional_class")
async def required_class(request: Request, student_id: int = None):
    user = util.getUser(request)
    enrollments = Enrollment.from_json(ENROLLMENTS_FILE)
    tmp = []
    if user == 0:
        user = student_id
    for enrollment in enrollments:
        if enrollment.id == user:
            for courseid in enrollment.course_id:
                courses = Course.from_json(COURSES_FILE)
                courseid = courseid - 1
                if not courses[courseid].required:
                    tmp.append(courses[courseid].id)
            return tmp

    raise HTTPException(status_code=404, detail="Student not found")


class search_payload(BaseModel):
    student_id: int = None
    query: str


@router.post("/search")
async def search(request: Request, payload: search_payload):
    user = util.getUser(request)
    enrollments = Enrollment.from_json(ENROLLMENTS_FILE)
    tmp = []
    if user == 0:
        user = payload.student_id
    print(payload.student_id)
    for enrollment in enrollments:
        if enrollment.id == payload.query:
            for courseid in enrollment.course_id:
                courses = Course.from_json(COURSES_FILE)
                courseid = courseid - 1
                tmp.append(courses[courseid].name)
            return tmp

    raise HTTPException(status_code=404, detail="Student not found")
