from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import json
from .courses import Course
from .enrollments import Enrollment
import util

router = APIRouter(prefix="/activity", tags=["activity"])

COURSES_FILE = 'courses.json'
ENROLLMENTS_FILE = 'enrollments.json'

week = ["","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]



class Activity(BaseModel):
    id: int = None
    name: str
    activity_type: str
    day: str
    hour: str
    owners: list[str] = None
    owner: str = None


def load_activities(file_path):
    with open(file_path) as f:
        data = json.load(f)

    activities = []
    for activity_data in data['activities']:
        activities.append(activity_data)

    return activities


def filter_activities(activities, activity_type=None, owner=None):
    filtered_activities = []
    for activity in activities:
        if activity_type and activity['activity_type'] != activity_type:
            continue
        if activity_type == 'Personal' and owner and activity['owner'] != owner:
            continue
        if activity_type == 'Group' and owner and activity['owners'] and int(owner) not in activity['owners']:
            continue
        filtered_activities.append(activity)
    return filtered_activities


def get_max_activity_id(activities):
    max_id = 0
    for activity in activities:
        if activity['id'] > max_id:
            max_id = activity['id']
    return max_id


def save_activities(activities, file_path):
    data = {
        'activities': activities
    }

    with open(file_path, 'w') as f:
        json.dump(data, f)


group_activities = load_activities('group_activities.json')
personal_activities = load_activities('personal_activities.json')


@router.get("/{activity_type}")
def get_activities(request: Request, activity_type: str = None,
                   owner: str = None):
    if util.getUser(request) != "0":
        owner = str(util.getUser(request))
    print(owner)
    filtered_group_activities = filter_activities(group_activities, activity_type=activity_type, owner=owner)
    filtered_personal_activities = filter_activities(personal_activities, activity_type=activity_type, owner=owner)
    filtered_activities = filtered_group_activities + filtered_personal_activities
    return filtered_activities


def check_conflict(day: int, hour: int, student_id: int):  # student_id course_id
    courses = Course.from_json(COURSES_FILE)
    enrollments = Enrollment.from_json(ENROLLMENTS_FILE)
    stu_course = []
    for enrollment in enrollments:
        if enrollment.id == student_id:
            stu_course = enrollment.course_id
    for course in stu_course:  # (origin)course compare with (target)course_id
        for i in courses[course].class_schedule:
            day=int(day)
            print(i)
            if i[0] == week[day]:
                for k in i[1]:
                    if k == int(hour):
                        return True
        return False


@router.post("/")
def create_activity(activity: dict):
    if activity['activity_type'] == "group":
        for i in activity['owners']:
            if check_conflict(activity['day'], activity['hour'], i):
                raise HTTPException(status_code=400, detail="Time conflict.")
    elif check_conflict(activity['day'], activity['hour'], activity['owner']):
        raise HTTPException(status_code=400, detail="Time conflict.")
    max_id = get_max_activity_id(group_activities)
    activity_type = activity.get('activity_type')
    if not activity_type or activity_type not in ["group", "personal"]:
        raise HTTPException(status_code=400, detail="Invalid activity type.")
    if activity_type == "group":
        file_path = 'group_activities.json'
        activities = load_activities(file_path)
        max_id = get_max_activity_id(activities)
        activity['id'] = max_id + 1
    elif activity_type == "personal":
        file_path = 'personal_activities.json'
        activities = load_activities(file_path)
        max_id = get_max_activity_id(activities)
        activity['id'] = max_id + 1

    activities = load_activities(file_path)
    activities.append(activity)
    save_activities(activities, file_path)

    return {"message": "Activity created successfully."}


@router.delete("/{activity_type}/{activity_id}")
def delete_activity(activity_id: int, activity_type: str):
    if activity_type == "group":
        file_path = 'group_activities.json'
    elif activity_type == "personal":
        file_path = 'personal_activities.json'
    else:
        raise HTTPException(status_code=400, detail="Invalid activity type.")

    activities = load_activities(file_path)
    filtered_activities = [activity for activity in activities if activity['id'] != activity_id]

    if len(activities) == len(filtered_activities):
        raise HTTPException(status_code=404, detail="Activity not found.")

    save_activities(filtered_activities, file_path)

    return {"message": "Activity deleted successfully."}
