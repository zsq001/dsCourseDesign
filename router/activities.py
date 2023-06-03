from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

import util

router = APIRouter(prefix="/activity", tags=["activity"])


class Activity(BaseModel):
    id: int
    name: str
    activity_type: str
    start_time: datetime
    end_time: datetime
    owners: list[str] = None
    owner: str = None


def load_activities(file_path):
    with open(file_path) as f:
        data = json.load(f)

    activities = []
    for activity_data in data['activities']:
        id = activity_data['id']
        name = activity_data['name']
        activity_type = activity_data['activity_type']
        start_time = datetime.strptime(activity_data['start_time'], '%Y-%m-%d %H:%M')
        end_time = datetime.strptime(activity_data['end_time'], '%Y-%m-%d %H:%M')
        owners = activity_data.get('owners')
        owner = activity_data.get('owner')
        activities.append(
            Activity(id=id, name=name, activity_type=activity_type, start_time=start_time, end_time=end_time,
                     owners=owners, owner=owner))

    return activities


def filter_activities(activities, start_time=None, end_time=None, activity_type=None, owner=None):
    filtered_activities = []

    for activity in activities:
        if start_time and activity.start_time < start_time:
            continue
        if end_time and activity.end_time > end_time:
            continue
        if activity_type and activity_type != activity.activity_type:
            continue
        if owner and activity.owners and (owner not in activity.owners):
            continue
        if owner and activity.owner and (owner != activity.owner):
            continue

        filtered_activities.append(activity)

    return filtered_activities



def sort_activities_by_start_time(activities):
    sorted_activities = sorted(activities, key=lambda x: x.start_time)
    return sorted_activities


def save_activities(activities, file_path):
    data = {
        'activities': [activity.dict() for activity in activities]
    }

    with open(file_path, 'w') as f:
        json.dump(data, f)


def validate_activity_time(activity):
    if activity.start_time.hour < 6 or activity.end_time.hour > 22:
        raise HTTPException(status_code=400, detail="Activity time should be between 6:00 and 22:00.")
    if activity.start_time.minute != 0 or activity.end_time.minute != 0:
        raise HTTPException(status_code=400,
                            detail="Activity start and end time should be at the beginning of the hour.")


group_activities = load_activities('group_activities.json')
personal_activities = load_activities('personal_activities.json')


@router.get("/{activity_type}")
def get_activities(request: Request, start_time: datetime = None, end_time: datetime = None, activity_type: str = None,
                   owner: str = None):
    if util.getUser(request) != "0":
        owner = str(util.getUser(request))
    print(owner)
    filtered_group_activities = filter_activities(group_activities, start_time=start_time, end_time=end_time,
                                                  activity_type=activity_type, owner=owner)
    filtered_personal_activities = filter_activities(personal_activities, start_time=start_time, end_time=end_time,
                                                     activity_type=activity_type, owner=owner)
    filtered_activities = filtered_group_activities + filtered_personal_activities
    sorted_activities = sort_activities_by_start_time(filtered_activities)
    return sorted_activities


@router.post("/")
def create_activity(activity: Activity):
    validate_activity_time(activity)
    if activity.activity_type == "Group":
        group_activities.append(activity)
        save_activities(group_activities, 'group_activities.json')
    elif activity.activity_type == "Personal":
        personal_activities.append(activity)
        save_activities(personal_activities, 'personal_activities.json')

    return {"message": "Activity created successfully."}


@router.delete("/activities/{activity_id}")
def delete_activity(activity_id: int, activity_type: Optional[str] = None):
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
