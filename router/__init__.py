# router/__init__.py

from fastapi import APIRouter
from . import users
from . import courses

router = APIRouter()
router.include_router(users.router)
router.include_router(courses.router)

