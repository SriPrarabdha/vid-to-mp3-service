
from datetime import datetime
from fastapi import FastAPI, Request, Response

from .api.auth import router as authentication_router
from ..db_util.db_conn import Base, engine



app = FastAPI(title="Video TO mp3 auth service")

app.include_router(authentication_router.router)

@app.get("/")
async def root():
    return {"message": "Hello from our video to mp3 service"}


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
