import json
from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import util
import re
import logging

tags_metadata = [
    {
        "name": "add_schedule",
        "description": "传入List[Dict[str, Any]]，(Optional)admin_person_id: str",
    },
    {
        "name": "get_schedule",
        "description": "传入(Optional)admin_person_id: str",
    },
    {
        "name": "delete_schedule",
        "description": "传入(Optional)admin_person_id: str",
    }

]

logger = logging.getLogger("daily")

router = APIRouter(prefix="/schedule", tags=["schedule"])

# 定义哈希表的大小
HASH_TABLE_SIZE = 100

# 定义哈希表的存储结构
hash_table = [None] * HASH_TABLE_SIZE

# JSON文件路径
json_file = "schedules.json"


class Schedule:
    def __init__(self, person_id, schedule):
        self.person_id = person_id
        self.schedule = schedule
        self.next = None


def hash_function(person_id):
    # 自定义哈希函数，将 person_id 映射到哈希表中的索引位置
    hash_value = sum(ord(c) for c in person_id) % HASH_TABLE_SIZE
    return hash_value


@router.on_event("startup")
def load_schedules():
    # 从JSON文件加载日程信息
    try:
        with open(json_file, "r") as file:
            data = json.load(file)
            print(data.items())
            for person_id, schedules, in data.items():
                index = hash_function(person_id)
                for schedule in schedules:
                    if not hash_table[index]:
                        hash_table[index] = Schedule(person_id, schedule)
                    else:
                        current = hash_table[index]
                        while current.next:
                            current = current.next
                        current.next = Schedule(person_id, schedule)
    except FileNotFoundError:
        # 如果文件不存在，创建一个空的哈希表
        pass


@router.on_event("shutdown")
def save_schedules():
    # 将日程信息保存到JSON文件
    data = {}
    for i in range(HASH_TABLE_SIZE):
        current = hash_table[i]
        while current:
            if current.person_id in data:
                data[current.person_id].append(current.schedule)
            else:
                data[current.person_id] = [current.schedule]
            current = current.next

    with open(json_file, "w") as file:
        json.dump(data, file)


@router.get("/", tags=["get_schedule"])
def get_schedule(request: Request, admin_person_id: str = None):
    person_id = util.getUser(request)
    if person_id == 0:
        person_id = admin_person_id
    logger.info(f"got schedule for {person_id}")
    index = hash_function(person_id)
    current = hash_table[index]
    tmp = []
    while current:
        if current.person_id == person_id:
            tmp.append(current.schedule)
        current = current.next
    if tmp:
        return tmp
    raise HTTPException(status_code=404, detail="user not found")


class add_schedule(BaseModel):
    schedule: List[Dict[str, Any]]
    admin_person_id: str = None


@router.post("/add_schedule", tags=["add_schedule"])
def add_schedule(request: Request, addschedule: add_schedule):
    person_id = util.getUser(request)
    if person_id == 0:
        person_id = addschedule.admin_person_id
    print(person_id)
    index = hash_function(person_id)
    logger.info(f"added schedule for {person_id}")
    if not hash_table[index]:
        hash_table[index] = Schedule(person_id, addschedule.schedule)
    else:
        current = hash_table[index]
        while current.next:
            current = current.next
        current.next = Schedule(person_id, addschedule.schedule)

    return {"message": "Schedule added successfully"}


def fuzzy_search_schedule(query, person_id):
    with open('schedules.json') as file:
        data = json.load(file)
    results = []
    person_id = str(person_id)
    if person_id in data:
        for schedule in data[person_id]:
            name = schedule["name"]
            if re.search(query, name, re.IGNORECASE):
                results.append(schedule)
    return results
class search_schedule(BaseModel):  # type-name/starts/ends
    query: str
    admin_person_id: str = None


@router.post("/search")
def search_schedule(request: Request, search: search_schedule):
    person_id = util.getUser(request)
    if person_id == 0:
        person_id = search.admin_person_id
    try:
        results = fuzzy_search_schedule(search.query, person_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="type not found")
    logger.info(f"searched schedule for {person_id}")
    return {"results": results}
