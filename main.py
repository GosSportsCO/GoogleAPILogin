from contextlib import asynccontextmanager
from fastapi import FastAPI
from db import database
from api_calls.routes import api_router

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await database.connect()
    try:
        yield
    finally:
        await database.disconnect()


app = FastAPI(lifespan=app_lifespan)
app.include_router(api_router)