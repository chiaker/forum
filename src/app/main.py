from fastapi import FastAPI
from src.api_v1.views import router
from src.api_v1.models import init_db

app = FastAPI()

init_db()

app.include_router(router, prefix="/api/v1")
