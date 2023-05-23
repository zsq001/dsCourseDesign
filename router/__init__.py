# router/__init__.py

from fastapi import APIRouter
from . import users
from . import courses
from . import enrollments
from . import schedule

router = APIRouter()
router.include_router(users.router)
router.include_router(courses.router)
router.include_router(enrollments.router)
router.include_router(schedule.router)


