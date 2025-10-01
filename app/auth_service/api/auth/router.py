from fastapi import APIRouter
from . import user_auth

router = APIRouter(prefix="/auth", tags=["auth"],)

router.include_router(user_auth.router)
