from fastapi import APIRouter, Cookie, HTTPException, Response, Body
from typing import List, Optional, Dict, Any, Union
import json

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

ENROLLMENTS_FILE = 'enrollments.json'

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

@router.get("/{student_id}")
async def get_enrollments(student_id: int):
    enrollments = Enrollment.from_json(ENROLLMENTS_FILE)
    for enrollment in enrollments:
        if enrollment.id == student_id:
            return enrollment.to_dict()


@router.post("/{student_id}/update_course")
async def update_course(student_id: int, course_id: List[int]):
    enrollments = Enrollment.from_json(ENROLLMENTS_FILE)
    for enrollment in enrollments:
        if enrollment.id == student_id:
            enrollment.course_id = course_id
            write_json({'students': [enrollment.to_dict() for enrollment in enrollments]}, ENROLLMENTS_FILE)
            return enrollment.to_dict()

    raise HTTPException(status_code=404, detail="Student not found")