from fastapi import APIRouter
from api_calls import auth

api_router = APIRouter()
api_router.include_router(auth.router)
