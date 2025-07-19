from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src_b.api_v1.views import router
from src_b.api_v1.models import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Лучше указать конкретный адрес в проде
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(router, prefix="/api/v1")
