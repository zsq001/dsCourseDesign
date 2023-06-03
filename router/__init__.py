# router/__init__.py

from fastapi import APIRouter
from . import users
from . import courses
from . import enrollments
from . import schedule
from . import maps
from . import activities

router = APIRouter()
router.include_router(users.router)
router.include_router(courses.router)
router.include_router(enrollments.router)
router.include_router(schedule.router)
router.include_router(maps.router)
router.include_router(activities.router)

